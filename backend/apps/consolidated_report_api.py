from io import BytesIO

from django.db.models import Avg
from django.http import FileResponse, JsonResponse
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.academics.models import AcademicYear, Classroom, Term
from apps.assessments.models import AssessmentSubmission, CompetencyEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.portfolio.models import PortfolioItem
from apps.reporting.pdf import build_document, data_table, footer, info_table, report_header, report_styles, summary_table


class ConsolidatedReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can access consolidated reports.")
        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")
        classroom_id = request.query_params.get("classroom")
        student_id = request.query_params.get("student")
        if not year_id or not term_id:
            return JsonResponse({"detail": "Academic year and term are required."}, status=400)

        year = AcademicYear.objects.filter(id=year_id).first()
        term = Term.objects.select_related("academic_year").filter(id=term_id, academic_year_id=year_id).first()
        if year is None or term is None:
            return JsonResponse({"detail": "The selected academic year or term was not found."}, status=404)

        classroom = None
        if classroom_id:
            classroom = Classroom.objects.select_related("school", "cambridge_stage").filter(id=classroom_id, is_active=True).first()
            if classroom is None:
                return JsonResponse({"detail": "Classroom not found."}, status=404)
            if school is not None and classroom.school_id != school.id:
                raise PermissionDenied("The classroom does not belong to your institution.")
            if classroom.academic_year_id != year.id or classroom.term_id != term.id:
                return JsonResponse({"detail": "The classroom does not belong to the selected academic period."}, status=400)

        enrollments = Enrollment.objects.select_related("student", "classroom").filter(
            academic_year_id=year.id, term_id=term.id, status__in=["ACTIVE", "COMPLETED"]
        )
        if school is not None:
            enrollments = enrollments.filter(classroom__school=school)
        if classroom is not None:
            enrollments = enrollments.filter(classroom=classroom)
        if student_id:
            enrollments = enrollments.filter(student_id=student_id)
        enrollments = enrollments.order_by("student__admission_number")
        if not enrollments.exists():
            return JsonResponse({"detail": "No matching enrolled students were found."}, status=404)

        enrollment_ids = list(enrollments.values_list("id", flat=True))
        submissions = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrollment_ids, evaluation__published=True, assessment__status="PUBLISHED"
        ).select_related("evaluation")
        assessment_scores = {}
        for row in submissions.values("enrollment_id").annotate(average=Avg("evaluation__percentage")):
            assessment_scores[row["enrollment_id"]] = row["average"]
        assessment_counts = {}
        for enrollment_id in submissions.values_list("enrollment_id", flat=True):
            assessment_counts[enrollment_id] = assessment_counts.get(enrollment_id, 0) + 1

        attendance = AttendanceRecord.objects.filter(enrollment_id__in=enrollment_ids)
        attendance_data = {}
        for enrollment_id in enrollment_ids:
            records = attendance.filter(enrollment_id=enrollment_id)
            total = records.count()
            attended = records.filter(status__in=["PRESENT", "LATE"]).count()
            attendance_data[enrollment_id] = round(attended * 100 / total, 1) if total else None

        competency_data = {}
        for item in CompetencyEvaluation.objects.filter(
            evaluation__submission__enrollment_id__in=enrollment_ids, evaluation__published=True
        ).values("evaluation__submission__enrollment_id", "level"):
            competency_data.setdefault(item["evaluation__submission__enrollment_id"], []).append(item["level"])

        portfolio_items = PortfolioItem.objects.filter(
            portfolio__student_id__in=enrollments.values_list("student_id", flat=True),
            event_date__gte=term.start_date,
            event_date__lte=term.end_date,
        ).prefetch_related("artifacts")
        portfolio_counts = {}
        artifact_counts = {}
        for item in portfolio_items:
            student_key = item.portfolio.student_id
            portfolio_counts[student_key] = portfolio_counts.get(student_key, 0) + 1
            artifact_counts[student_key] = artifact_counts.get(student_key, 0) + item.artifacts.count()

        rows = []
        total_scores, attendance_rates, competency_proficient = [], [], []
        total_items = total_artifacts = 0
        for enrollment in enrollments:
            score = assessment_scores.get(enrollment.id)
            attendance_rate = attendance_data.get(enrollment.id)
            levels = competency_data.get(enrollment.id, [])
            proficient = round(sum(level in {"PROFICIENT", "ADVANCED"} for level in levels) * 100 / len(levels), 1) if levels else None
            items = portfolio_counts.get(enrollment.student_id, 0)
            artifacts = artifact_counts.get(enrollment.student_id, 0)
            rows.append([
                enrollment.student.admission_number,
                str(enrollment.student),
                f"{float(score):.1f}%" if score is not None else "—",
                f"{attendance_rate:.1f}%" if attendance_rate is not None else "—",
                f"{proficient:.1f}%" if proficient is not None else "—",
                str(assessment_counts.get(enrollment.id, 0)),
                str(items),
                str(artifacts),
            ])
            if score is not None:
                total_scores.append(float(score))
            if attendance_rate is not None:
                attendance_rates.append(attendance_rate)
            if proficient is not None:
                competency_proficient.append(proficient)
            total_items += items
            total_artifacts += artifacts

        summary = {
            "students": len(rows),
            "assessment_average": sum(total_scores) / len(total_scores) if total_scores else None,
            "attendance_average": sum(attendance_rates) / len(attendance_rates) if attendance_rates else None,
            "competency_average": sum(competency_proficient) / len(competency_proficient) if competency_proficient else None,
            "portfolio_items": total_items,
            "artifacts": total_artifacts,
        }
        return self._build_pdf(school, classroom, year, term, summary, rows)

    def _build_pdf(self, school, classroom, year, term, summary, rows):
        buffer = BytesIO()
        doc = build_document(buffer, landscape_mode=True, title="Consolidated Academic Report")
        styles = report_styles()
        story = []
        report_header(
            story,
            school.name if school else "KEY",
            "Consolidated Academic Report",
            f"{year.name} • Term {term.term_number}",
        )
        scope = classroom.name if classroom else "All Classes"
        stage = classroom.cambridge_stage.name if classroom and classroom.cambridge_stage else "—"
        story.extend([
            info_table([
                ["Scope", scope, "Academic Year", year.name, "Term", f"Term {term.term_number}"],
                ["Stage", stage, "Students", str(summary["students"]), "Generated By", "KEY"],
            ], [24 * mm, 48 * mm, 32 * mm, 42 * mm, 22 * mm, 42 * mm]),
            Spacer(1, 4 * mm),
            summary_table(
                [
                    "Students", str(summary["students"]),
                    "Assessment Avg", f"{summary['assessment_average']:.1f}%" if summary["assessment_average"] is not None else "—",
                    "Attendance Avg", f"{summary['attendance_average']:.1f}%" if summary["attendance_average"] is not None else "—",
                    "Competency Proficient+", f"{summary['competency_average']:.1f}%" if summary["competency_average"] is not None else "—",
                    "Portfolio Items", str(summary["portfolio_items"]),
                    "Artifacts", str(summary["artifacts"]),
                ],
                [21 * mm, 18 * mm, 29 * mm, 21 * mm, 29 * mm, 21 * mm, 38 * mm, 24 * mm, 27 * mm, 18 * mm, 21 * mm, 18 * mm],
            ),
            Paragraph("Learner Performance", styles["heading"]),
            data_table(
                [["Admission", "Student", "Assessment Avg", "Attendance", "Competency P+", "Assessments", "Portfolio", "Artifacts"]] + rows,
                [25 * mm, 65 * mm, 29 * mm, 27 * mm, 30 * mm, 25 * mm, 25 * mm, 25 * mm],
                center_from=2,
            ),
            Spacer(1, 5 * mm),
            Paragraph(
                "This consolidated report combines published assessment performance, attendance, competency outcomes, and portfolio evidence counts for the selected academic period.",
                styles["small"],
            ),
        ])
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"consolidated-report-{year.name}-term-{term.term_number}.pdf",
            content_type="application/pdf",
        )

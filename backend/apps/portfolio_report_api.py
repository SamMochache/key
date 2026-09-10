from collections import defaultdict
from io import BytesIO

from django.http import FileResponse, JsonResponse
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.academics.models import Classroom
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school, teacher_can_access_classroom
from apps.enrollment.models import Enrollment
from apps.portfolio.models import PortfolioItem
from apps.reporting.pdf import build_document, data_table, footer, info_table, report_header, report_styles, summary_table
from core.constants.enrollment import EnrollmentStatus


class PortfolioEvidenceReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can access portfolio reports.")

        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        classroom_id = request.query_params.get("classroom")
        student_id = request.query_params.get("student")
        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")

        classroom = None
        if classroom_id:
            classroom = Classroom.objects.select_related(
                "school", "academic_year", "term", "cambridge_stage"
            ).filter(id=classroom_id, is_active=True).first()
            if classroom is None:
                return JsonResponse({"detail": "Classroom not found."}, status=404)
            if school is not None and classroom.school_id != school.id:
                raise PermissionDenied("The classroom does not belong to your institution.")
            if role == UserRole.TEACHER and not teacher_can_access_classroom(request.user, classroom.id):
                raise PermissionDenied("You are not assigned to this classroom.")
            if year_id and str(classroom.academic_year_id) != year_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected academic year."}, status=400)
            if term_id and str(classroom.term_id) != term_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected term."}, status=400)

        enrollments = Enrollment.objects.select_related(
            "student", "classroom", "classroom__school", "academic_year", "term"
        ).filter(status__in=[EnrollmentStatus.ENROLLED, EnrollmentStatus.PROMOTED])
        if school is not None:
            enrollments = enrollments.filter(classroom__school=school)
        if classroom is not None:
            enrollments = enrollments.filter(classroom=classroom)
        if role == UserRole.TEACHER:
            enrollments = enrollments.filter(
                classroom__teacher_assignments__teacher=request.user.teacher_profile,
                classroom__teacher_assignments__is_active=True,
            )
        if year_id:
            enrollments = enrollments.filter(academic_year_id=year_id)
        if term_id:
            enrollments = enrollments.filter(term_id=term_id)
        if student_id:
            enrollments = enrollments.filter(student_id=student_id)
        enrollments = enrollments.order_by("student__admission_number").distinct()

        if not enrollments.exists():
            return JsonResponse({"detail": "No matching enrolled students were found."}, status=404)

        enrollment_ids = list(enrollments.values_list("id", flat=True))
        items = PortfolioItem.objects.filter(
            portfolio__student_id__in=enrollments.values_list("student_id", flat=True),
        ).select_related(
            "portfolio__student__user",
            "assessment_submission__assessment",
            "assessment_submission__enrollment",
            "lesson_session",
        ).prefetch_related("artifacts")

        if term_id:
            selected_term = enrollments.first().term
            items = items.filter(event_date__gte=selected_term.start_date, event_date__lte=selected_term.end_date)
        elif year_id:
            selected_year = enrollments.first().academic_year
            items = items.filter(event_date__gte=selected_year.start_date, event_date__lte=selected_year.end_date)
        if classroom is not None:
            items = items.filter(portfolio__student__enrollments__classroom=classroom).distinct()

        items_by_student = defaultdict(list)
        for item in items:
            items_by_student[str(item.portfolio.student_id)].append(item)

        evaluations = AssessmentEvaluation.objects.filter(
            published=True,
            submission__enrollment_id__in=enrollment_ids,
        ).select_related("submission__assessment", "submission__enrollment__student")
        evaluation_ids = set(evaluations.values_list("submission_id", flat=True))

        rows = []
        item_rows = []
        total_items = 0
        total_artifacts = 0
        total_assessments = set()
        total_lessons = set()

        for enrollment in enrollments:
            student_items = items_by_student.get(str(enrollment.student_id), [])
            published_assessment_ids = set()
            lesson_ids = set()
            artifact_count = 0
            for item in student_items:
                artifact_count += len(item.artifacts.all())
                if item.assessment_submission_id and item.assessment_submission_id in evaluation_ids:
                    published_assessment_ids.add(item.assessment_submission_id)
                if item.lesson_session_id:
                    lesson_ids.add(item.lesson_session_id)
                item_rows.append([
                    enrollment.student.admission_number,
                    str(enrollment.student),
                    item.title,
                    item.get_item_type_display(),
                    item.event_date.strftime("%d %b %Y"),
                    str(len(item.artifacts.all())),
                ])
            total_assessments.update(published_assessment_ids)
            total_lessons.update(lesson_ids)
            total_items += len(student_items)
            total_artifacts += artifact_count
            rows.append([
                enrollment.student.admission_number,
                str(enrollment.student),
                str(len(student_items)),
                str(artifact_count),
                str(len(published_assessment_ids)),
                str(len(lesson_ids)),
            ])

        summary = {
            "students": enrollments.count(),
            "items": total_items,
            "artifacts": total_artifacts,
            "assessments": len(total_assessments),
            "lessons": len(total_lessons),
        }
        return self._build_pdf(school, classroom, summary, rows, item_rows)

    def _build_pdf(self, school, classroom, summary, rows, item_rows):
        buffer = BytesIO()
        doc = build_document(buffer, landscape_mode=True, title="Portfolio & Evidence Summary")
        styles = report_styles()
        story = []
        school_name = school.name if school else (classroom.school.name if classroom else "KEY")
        subtitle = "Institution-wide scope"
        if classroom:
            subtitle = f"{classroom.name} • {classroom.academic_year.name} • Term {classroom.term.term_number}"

        report_header(story, school_name, "Portfolio & Evidence Summary", subtitle)

        if classroom:
            stage = classroom.cambridge_stage.name if classroom.cambridge_stage else "—"
            story.extend([
                info_table([
                    ["Class", classroom.name, "Code", classroom.code, "Stage", stage],
                    ["Academic Year", classroom.academic_year.name, "Term", f"Term {classroom.term.term_number}", "Students", str(summary["students"])],
                ], [25 * mm, 55 * mm, 22 * mm, 45 * mm, 22 * mm, 55 * mm]),
                Spacer(1, 4 * mm),
            ])

        story.extend([
            summary_table(
                ["Students", str(summary["students"]), "Portfolio Items", str(summary["items"]), "Artifacts", str(summary["artifacts"]), "Assessments", str(summary["assessments"]), "Lessons", str(summary["lessons"])],
                [25 * mm, 22 * mm, 32 * mm, 22 * mm, 24 * mm, 22 * mm, 27 * mm, 22 * mm, 20 * mm, 22 * mm],
            ),
            Paragraph("Student Portfolio Summary", styles["heading"]),
            data_table(
                [["Admission", "Student", "Items", "Artifacts", "Published Assessments", "Lessons"]] + rows,
                [30 * mm, 70 * mm, 22 * mm, 25 * mm, 40 * mm, 25 * mm],
                center_from=2,
            ),
            Paragraph("Portfolio Evidence", styles["heading"]),
            data_table(
                [["Admission", "Student", "Portfolio Item", "Type", "Date", "Artifacts"]] + item_rows,
                [28 * mm, 60 * mm, 80 * mm, 35 * mm, 30 * mm, 25 * mm],
                font_size=7.5,
                center_from=5,
            ),
            Spacer(1, 5 * mm),
            Paragraph(
                "This report summarizes portfolio items and attached evidence within the selected enrollment and academic-period scope. Published assessment references are counted only when a published evaluation exists.",
                styles["small"],
            ),
        ])
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"portfolio-evidence-{classroom.code if classroom else 'report'}.pdf", content_type="application/pdf")

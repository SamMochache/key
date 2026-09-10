from io import BytesIO

from django.db.models import Avg, Count, Q
from django.http import FileResponse, JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from apps.academics.models import Classroom
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school, teacher_can_access_classroom
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.reporting.pdf import build_document, data_table, footer, info_table, report_header, report_styles, summary_table


class ClassReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can access class reports.")
        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        classroom_id = request.query_params.get("classroom")
        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")
        if not classroom_id:
            return JsonResponse({"detail": "A valid classroom is required."}, status=400)

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

        published_evaluations = AssessmentEvaluation.objects.filter(
            published=True,
            submission__enrollment__classroom=classroom,
            submission__enrollment__academic_year=classroom.academic_year,
            submission__enrollment__term=classroom.term,
        )
        evaluation_summary = published_evaluations.aggregate(
            average=Avg("percentage"),
            count=Count("id"),
        )

        enrollments = list(
            Enrollment.objects.filter(
                classroom=classroom,
                academic_year=classroom.academic_year,
                term=classroom.term,
            )
            .select_related("student", "student__user")
            .annotate(
                assessment_average=Avg(
                    "assessment_submissions__evaluations__percentage",
                    filter=Q(assessment_submissions__evaluations__published=True),
                ),
                result_count=Count(
                    "assessment_submissions__evaluations",
                    filter=Q(assessment_submissions__evaluations__published=True),
                    distinct=True,
                ),
                attendance_total=Count("attendance_records", distinct=True),
                attendance_credited=Count(
                    "attendance_records",
                    filter=Q(attendance_records__status__in=["PRESENT", "LATE"]),
                    distinct=True,
                ),
            )
            .order_by("student__admission_number")
        )

        rows = []
        class_attendance_total = sum(enrollment.attendance_total for enrollment in enrollments)
        class_attendance_credited = sum(enrollment.attendance_credited for enrollment in enrollments)
        for enrollment in enrollments:
            attendance_rate = (
                round(enrollment.attendance_credited / enrollment.attendance_total * 100, 1)
                if enrollment.attendance_total
                else None
            )
            rows.append([
                enrollment.student.admission_number,
                str(enrollment.student),
                f"{enrollment.assessment_average:.1f}%" if enrollment.assessment_average is not None else "—",
                f"{attendance_rate:.1f}%" if attendance_rate is not None else "—",
                str(enrollment.result_count),
            ])

        class_average = evaluation_summary["average"]
        class_attendance = (
            round(class_attendance_credited / class_attendance_total * 100, 1)
            if class_attendance_total
            else None
        )

        buffer = BytesIO()
        doc = build_document(buffer, landscape_mode=True, title=f"Class Academic Report - {classroom.name}")
        styles = report_styles()
        story = []
        report_header(
            story,
            classroom.school.name,
            "Class Academic Report",
            f"{classroom.academic_year.name} • Term {classroom.term.term_number}",
        )
        story.append(info_table([
            ["Class", classroom.name, "Code", classroom.code, "Stage", classroom.cambridge_stage.name],
            ["Academic Year", classroom.academic_year.name, "Term", f"Term {classroom.term.term_number}", "Students", str(len(rows))],
        ], [25 * mm, 55 * mm, 22 * mm, 45 * mm, 22 * mm, 55 * mm]))
        story.append(Spacer(1, 4 * mm))
        story.append(summary_table([
            "Class Average", f"{class_average:.1f}%" if class_average is not None else "—",
            "Attendance", f"{class_attendance:.1f}%" if class_attendance is not None else "—",
            "Published Results", str(evaluation_summary["count"] or 0),
        ], [34 * mm, 35 * mm, 30 * mm, 35 * mm, 40 * mm, 35 * mm]))
        story.append(Paragraph("Student Performance", styles["heading"]))
        table_data = [["Admission", "Student", "Assessment Average", "Attendance", "Results"]] + rows
        if len(table_data) == 1:
            table_data.append(["—", "No enrolled students", "—", "—", "0"])
        story.extend([
            data_table(table_data, [35 * mm, 80 * mm, 45 * mm, 40 * mm, 30 * mm], center_from=2),
            Spacer(1, 6 * mm),
            Paragraph(
                "This report contains published assessment and attendance records available in KEY for the selected class, academic year, and term.",
                styles["small"],
            ),
        ])
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"class-report-{classroom.code}-{classroom.academic_year.name}-term-{classroom.term.term_number}.pdf",
            content_type="application/pdf",
        )

from io import BytesIO

from django.http import FileResponse, JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from apps.academics.models import Classroom
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.reporting.pdf import build_document, data_table, footer, info_table, report_header, report_styles, summary_table


class AttendanceReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can access attendance reports.")

        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        classroom_id = request.query_params.get("classroom")
        student_id = request.query_params.get("student")
        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")

        if not classroom_id and not student_id:
            return JsonResponse({"detail": "A classroom or student is required."}, status=400)

        enrollments = Enrollment.objects.select_related(
            "student", "student__user", "classroom", "academic_year", "term"
        )
        if school is not None:
            enrollments = enrollments.filter(student__school=school)
        if classroom_id:
            enrollments = enrollments.filter(classroom_id=classroom_id)
        if student_id:
            enrollments = enrollments.filter(student_id=student_id)
        if year_id:
            enrollments = enrollments.filter(academic_year_id=year_id)
        if term_id:
            enrollments = enrollments.filter(term_id=term_id)

        enrollments = enrollments.order_by("student__admission_number")
        if not enrollments.exists():
            return JsonResponse({"detail": "No enrollment found for the selected period."}, status=404)

        selected_classroom = enrollments.first().classroom
        if classroom_id:
            classroom = Classroom.objects.filter(id=classroom_id, is_active=True).select_related(
                "academic_year", "term", "cambridge_stage", "school"
            ).first()
            if classroom is None:
                return JsonResponse({"detail": "Classroom not found."}, status=404)
            if school is not None and classroom.school_id != school.id:
                raise PermissionDenied("The classroom does not belong to your institution.")
            if year_id and str(classroom.academic_year_id) != year_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected academic year."}, status=400)
            if term_id and str(classroom.term_id) != term_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected term."}, status=400)
            selected_classroom = classroom

        rows = []
        totals = {"PRESENT": 0, "ABSENT": 0, "LATE": 0, "EXCUSED": 0}
        total_records = 0
        total_credited = 0

        for enrollment in enrollments:
            records = AttendanceRecord.objects.filter(enrollment=enrollment)
            counts = {
                status: records.filter(status=status).count()
                for status in ("PRESENT", "LATE", "ABSENT", "EXCUSED")
            }
            total = sum(counts.values())
            credited = counts["PRESENT"] + counts["LATE"]
            rate = round(credited / total * 100, 1) if total else None
            for status, count in counts.items():
                totals[status] += count
            total_records += total
            total_credited += credited
            rows.append([
                enrollment.student.admission_number,
                str(enrollment.student),
                str(counts["PRESENT"]),
                str(counts["LATE"]),
                str(counts["ABSENT"]),
                str(counts["EXCUSED"]),
                f"{rate:.1f}%" if rate is not None else "—",
            ])

        overall_rate = round(total_credited / total_records * 100, 1) if total_records else None
        buffer = BytesIO()
        doc = build_document(buffer, landscape_mode=True, title="Attendance Summary Report")
        styles = report_styles()
        school_name = selected_classroom.school.name if getattr(selected_classroom, "school", None) else (school.name if school else "KEY")
        report_header(
            story := [],
            school_name,
            "Attendance Summary Report",
            f"{selected_classroom.name} • {selected_classroom.academic_year.name} • Term {selected_classroom.term.term_number}",
        )
        story.extend([
            info_table([
                ["Class", selected_classroom.name, "Code", selected_classroom.code, "Students", str(len(rows))],
                ["Academic Year", selected_classroom.academic_year.name, "Term", f"Term {selected_classroom.term.term_number}", "Attendance Records", str(total_records)],
            ], [25 * mm, 55 * mm, 22 * mm, 45 * mm, 30 * mm, 55 * mm]),
            Spacer(1, 4 * mm),
            summary_table([
                "Overall Rate", f"{overall_rate:.1f}%" if overall_rate is not None else "—",
                "Present", str(totals["PRESENT"]), "Late", str(totals["LATE"]),
                "Absent", str(totals["ABSENT"]), "Excused", str(totals["EXCUSED"]),
            ], [28 * mm, 30 * mm, 25 * mm, 25 * mm, 22 * mm, 25 * mm, 30 * mm]),
            Paragraph("Student Attendance", styles["heading"]),
            data_table(
                [["Admission", "Student", "Present", "Late", "Absent", "Excused", "Attendance Rate"]] + rows,
                [30 * mm, 80 * mm, 27 * mm, 25 * mm, 27 * mm, 28 * mm, 40 * mm],
                center_from=2,
            ),
            Spacer(1, 6 * mm),
            Paragraph(
                "Attendance rate counts Present and Late records as attended. Excused records are reported separately and are not counted as attended.",
                styles["small"],
            ),
        ])
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buffer.seek(0)
        filename = f"attendance-report-{selected_classroom.code}-{selected_classroom.academic_year.name}-term-{selected_classroom.term.term_number}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type="application/pdf")

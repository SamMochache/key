from io import BytesIO

from django.http import FileResponse, JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.academics.models import AcademicYear, Classroom, Term
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment


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

        classrooms = Classroom.objects.select_related("school", "academic_year", "term", "cambridge_stage")
        classroom = classrooms.filter(id=classroom_id, is_active=True).first()
        if classroom is None:
            return JsonResponse({"detail": "Classroom not found."}, status=404)
        if school is not None and classroom.school_id != school.id:
            raise PermissionDenied("The classroom does not belong to your institution.")
        if year_id and str(classroom.academic_year_id) != year_id:
            return JsonResponse({"detail": "The classroom does not belong to the selected academic year."}, status=400)
        if term_id and str(classroom.term_id) != term_id:
            return JsonResponse({"detail": "The classroom does not belong to the selected term."}, status=400)

        enrollments = Enrollment.objects.filter(
            classroom=classroom,
            academic_year=classroom.academic_year,
            term=classroom.term,
        ).select_related("student", "student__user").order_by("student__admission_number")

        evaluation_qs = AssessmentEvaluation.objects.filter(
            published=True,
            submission__enrollment__classroom=classroom,
            submission__enrollment__academic_year=classroom.academic_year,
            submission__enrollment__term=classroom.term,
        )

        rows = []
        class_scores = []
        class_attendance_total = 0
        class_attendance_present = 0

        for enrollment in enrollments:
            scores = [
                float(value)
                for value in evaluation_qs.filter(submission__enrollment=enrollment).values_list("percentage", flat=True)
                if value is not None
            ]
            average = round(sum(scores) / len(scores), 1) if scores else None

            attendance = AttendanceRecord.objects.filter(enrollment=enrollment)
            total = attendance.count()
            present = attendance.filter(status__in=["PRESENT", "LATE"]).count()
            attendance_rate = round(present / total * 100, 1) if total else None

            if average is not None:
                class_scores.extend(scores)
            class_attendance_total += total
            class_attendance_present += present

            rows.append([
                enrollment.student.admission_number,
                str(enrollment.student),
                f"{average:.1f}%" if average is not None else "—",
                f"{attendance_rate:.1f}%" if attendance_rate is not None else "—",
                str(len(scores)),
            ])

        class_average = round(sum(class_scores) / len(class_scores), 1) if class_scores else None
        class_attendance = round(class_attendance_present / class_attendance_total * 100, 1) if class_attendance_total else None

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=f"Class Academic Report - {classroom.name}",
            author="KEY",
        )
        styles = getSampleStyleSheet()
        title = ParagraphStyle(
            "ClassReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            leading=22,
            spaceAfter=4 * mm,
        )
        heading = ParagraphStyle(
            "ClassReportHeading",
            parent=styles["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        )
        small = ParagraphStyle("ClassReportSmall", parent=styles["BodyText"], fontSize=8, leading=10)

        story = [
            Paragraph("KEY", title),
            Paragraph("Class Academic Report", styles["Heading1"]),
            Spacer(1, 2 * mm),
        ]

        info = [
            ["Class", classroom.name, "Code", classroom.code, "Stage", classroom.cambridge_stage.name],
            ["Academic Year", classroom.academic_year.name, "Term", f"Term {classroom.term.term_number}", "Students", str(len(rows))],
        ]
        info_table = Table(info, colWidths=[25 * mm, 55 * mm, 22 * mm, 45 * mm, 22 * mm, 55 * mm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTNAME", (4, 0), (4, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f1f5f9")),
            ("BACKGROUND", (4, 0), (4, -1), colors.HexColor("#f1f5f9")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([info_table, Spacer(1, 4 * mm)])

        summary = [[
            "Class Average", f"{class_average:.1f}%" if class_average is not None else "—",
            "Attendance", f"{class_attendance:.1f}%" if class_attendance is not None else "—",
            "Published Results", str(len(class_scores)),
        ]]
        summary_table = Table(summary, colWidths=[34 * mm, 35 * mm, 30 * mm, 35 * mm, 40 * mm, 35 * mm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([summary_table, Paragraph("Student Performance", heading)])

        table_data = [["Admission", "Student", "Assessment Average", "Attendance", "Results"]] + rows
        if len(table_data) == 1:
            table_data.append(["—", "No enrolled students", "—", "—", "0"])
        student_table = Table(table_data, colWidths=[35 * mm, 80 * mm, 45 * mm, 40 * mm, 30 * mm], repeatRows=1)
        student_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([
            student_table,
            Spacer(1, 6 * mm),
            Paragraph(
                "This report contains published assessment and attendance records available in KEY for the selected class, academic year, and term.",
                small,
            ),
        ])
        doc.build(story)
        buffer.seek(0)
        filename = f"class-report-{classroom.code}-{classroom.academic_year.name}-term-{classroom.term.term_number}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type="application/pdf")

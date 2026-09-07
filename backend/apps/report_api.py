from io import BytesIO

from django.db.models import Avg
from django.http import FileResponse, JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.academics.models import AcademicYear, Term
from apps.assessments.models import AssessmentEvaluation, AssessmentSubmission, CompetencyEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.students.models import Student


COMPETENCY_LABELS = {
    "BEGINNING": "Beginning",
    "DEVELOPING": "Developing",
    "PROFICIENT": "Proficient",
    "ADVANCED": "Advanced",
}


class StudentReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT}:
            raise PermissionDenied("Your account does not have report access.")

        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        student_id = request.query_params.get("student")
        if role == UserRole.STUDENT:
            student = Student.objects.filter(user=request.user, is_active=True).first()
            if student_id and (student is None or str(student.id) != student_id):
                raise PermissionDenied("Students may only access their own report.")
        else:
            student = Student.objects.filter(id=student_id, is_active=True).first()

        if student is None:
            return JsonResponse({"detail": "A valid student is required."}, status=400)
        if school is not None and student.school_id != school.id:
            raise PermissionDenied("The student does not belong to your institution.")

        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")

        enrollments = Enrollment.objects.filter(student=student).select_related(
            "classroom", "academic_year", "term"
        )
        if year_id:
            enrollments = enrollments.filter(academic_year_id=year_id)
        if term_id:
            enrollments = enrollments.filter(term_id=term_id)
        enrollment = enrollments.order_by("-term__start_date").first()
        if enrollment is None:
            return JsonResponse({"detail": "No enrollment found for the selected period."}, status=404)

        enrollment_ids = Enrollment.objects.filter(
            student=student,
            academic_year=enrollment.academic_year,
            term=enrollment.term,
        ).values_list("id", flat=True)

        submissions = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrollment_ids,
            assessment__lesson_session__timetable_entry__timetable__term=enrollment.term,
            evaluation__published=True,
        ).select_related(
            "assessment",
            "evaluation",
            "assessment__lesson_session__timetable_entry__teacher_subject__subject",
        ).order_by("assessment__lesson_session__lesson_date")

        attendance = AttendanceRecord.objects.filter(
            enrollment_id__in=enrollment_ids
        )
        total_attendance = attendance.count()
        present = attendance.filter(status__in=["PRESENT", "LATE"]).count()
        attendance_rate = round((present / total_attendance) * 100, 1) if total_attendance else None

        scores = [float(value) for value in submissions.values_list("evaluation__percentage", flat=True) if value is not None]
        overall_average = round(sum(scores) / len(scores), 1) if scores else None

        competencies = CompetencyEvaluation.objects.filter(
            evaluation__submission__enrollment_id__in=enrollment_ids,
            evaluation__published=True,
        ).select_related("competency")
        competency_data = {}
        for item in competencies:
            competency_data.setdefault(item.competency.name, []).append(item.level)

        competency_rows = []
        scale = {"BEGINNING": 1, "DEVELOPING": 2, "PROFICIENT": 3, "ADVANCED": 4}
        for name, levels in sorted(competency_data.items())[:12]:
            valid = [scale[level] for level in levels if level in scale]
            if valid:
                average = sum(valid) / len(valid)
                level = min(scale, key=lambda key: abs(scale[key] - average))
                competency_rows.append((name, COMPETENCY_LABELS[level]))

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title=f"Student Academic Report - {student}",
            author="KEY",
        )
        styles = getSampleStyleSheet()
        title = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            leading=22,
            spaceAfter=5 * mm,
        )
        small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8.5, leading=11)
        heading = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=11, leading=14, spaceBefore=4 * mm, spaceAfter=2 * mm)

        story = [
            Paragraph("KEY", title),
            Paragraph("Student Academic Progress Report", styles["Heading1"]),
            Spacer(1, 3 * mm),
        ]

        info = [
            ["Student", str(student), "Admission", student.admission_number],
            ["Institution", student.school.name, "Class", enrollment.classroom.name],
            ["Academic Year", enrollment.academic_year.name, "Term", f"Term {enrollment.term.term_number}"],
        ]
        info_table = Table(info, colWidths=[28 * mm, 67 * mm, 28 * mm, 57 * mm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f1f5f9")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([info_table, Spacer(1, 5 * mm)])

        summary = [
            ["Overall Average", f"{overall_average:.1f}%" if overall_average is not None else "—", "Attendance", f"{attendance_rate:.1f}%" if attendance_rate is not None else "—", "Assessments", str(len(submissions))],
        ]
        summary_table = Table(summary, colWidths=[31 * mm, 27 * mm, 25 * mm, 27 * mm, 28 * mm, 42 * mm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.extend([summary_table, Paragraph("Assessment Results", heading)])

        result_data = [["Assessment", "Subject", "Date", "Score"]]
        for submission in submissions:
            subject = submission.assessment.lesson_session.timetable_entry.teacher_subject.subject.name
            percentage = submission.evaluation.percentage
            result_data.append([
                submission.assessment.title,
                subject,
                submission.assessment.lesson_session.lesson_date.strftime("%d %b %Y"),
                f"{float(percentage):.1f}%" if percentage is not None else "—",
            ])
        if len(result_data) == 1:
            result_data.append(["No published assessment results", "—", "—", "—"])
        results_table = Table(result_data, colWidths=[62 * mm, 43 * mm, 35 * mm, 20 * mm], repeatRows=1)
        results_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(results_table)

        story.append(Paragraph("Competency Outcomes", heading))
        competency_table_data = [["Competency", "Reported Level"]] + competency_rows
        if len(competency_table_data) == 1:
            competency_table_data.append(["No competency evaluations recorded", "—"])
        competency_table = Table(competency_table_data, colWidths=[125 * mm, 35 * mm], repeatRows=1)
        competency_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(competency_table)

        story.extend([
            Spacer(1, 8 * mm),
            Paragraph(
                "This report contains published academic, attendance, and competency records available in KEY for the selected academic period.",
                small,
            ),
        ])
        doc.build(story)
        buffer.seek(0)
        filename = f"student-report-{student.admission_number}-{enrollment.academic_year.name}-term-{enrollment.term.term_number}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type="application/pdf")

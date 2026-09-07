from collections import defaultdict
from io import BytesIO

from django.http import FileResponse, JsonResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.academics.models import Classroom
from apps.assessments.models import CompetencyEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.enrollment.models import Enrollment
from core.constants.competency import CompetencyLevel


LEVEL_ORDER = {
    CompetencyLevel.BEGINNING: 1,
    CompetencyLevel.DEVELOPING: 2,
    CompetencyLevel.PROFICIENT: 3,
    CompetencyLevel.ADVANCED: 4,
}
LEVEL_LABELS = dict(CompetencyLevel.choices)


class CompetencyOutcomesReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can access competency reports.")

        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        classroom_id = request.query_params.get("classroom")
        student_id = request.query_params.get("student")
        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")

        classroom = None
        if classroom_id:
            classroom = Classroom.objects.select_related("school", "academic_year", "term", "cambridge_stage").filter(
                id=classroom_id, is_active=True
            ).first()
            if classroom is None:
                return JsonResponse({"detail": "Classroom not found."}, status=404)
            if school is not None and classroom.school_id != school.id:
                raise PermissionDenied("The classroom does not belong to your institution.")
            if year_id and str(classroom.academic_year_id) != year_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected academic year."}, status=400)
            if term_id and str(classroom.term_id) != term_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected term."}, status=400)

        enrollments = Enrollment.objects.select_related("student", "classroom", "classroom__school", "classroom__academic_year", "classroom__term")
        if school is not None:
            enrollments = enrollments.filter(classroom__school=school)
        if classroom is not None:
            enrollments = enrollments.filter(classroom=classroom)
        if year_id:
            enrollments = enrollments.filter(academic_year_id=year_id)
        if term_id:
            enrollments = enrollments.filter(term_id=term_id)
        if student_id:
            enrollments = enrollments.filter(student_id=student_id)
        enrollments = enrollments.order_by("student__admission_number")

        if not enrollments.exists():
            return JsonResponse({"detail": "No matching enrolled students were found."}, status=404)

        enrollment_ids = list(enrollments.values_list("id", flat=True))
        evaluations = CompetencyEvaluation.objects.filter(
            evaluation__published=True,
            evaluation__submission__enrollment_id__in=enrollment_ids,
            evaluation__submission__assessment__status="PUBLISHED",
            competency__is_active=True,
        ).select_related(
            "competency",
            "evaluation__submission__enrollment__student",
            "evaluation__submission__assessment",
        ).order_by("competency__sequence", "evaluation__submission__enrollment__student__admission_number")

        if classroom is not None:
            evaluations = evaluations.filter(
                evaluation__submission__assessment__lesson_session__timetable_entry__teacher_subject__classroom=classroom
            )

        competencies = {}
        outcomes = defaultdict(dict)
        competency_values = defaultdict(list)
        distribution = defaultdict(int)

        for item in evaluations:
            competency_id = str(item.competency_id)
            competencies[competency_id] = item.competency
            enrollment_key = str(item.evaluation.submission.enrollment_id)
            level = item.level
            outcomes[enrollment_key][competency_id] = level
            if level in LEVEL_ORDER:
                competency_values[competency_id].append(LEVEL_ORDER[level])
                distribution[level] += 1

        competency_list = sorted(competencies.values(), key=lambda value: (value.sequence, value.name))
        total_levels = sum(distribution.values())
        rows = []
        for enrollment in enrollments:
            enrollment_key = str(enrollment.id)
            for competency in competency_list:
                rows.append([
                    enrollment.student.admission_number,
                    str(enrollment.student),
                    competency.name,
                    LEVEL_LABELS.get(outcomes[enrollment_key].get(str(competency.id)), "—"),
                ])
            if not competency_list:
                rows.append([enrollment.student.admission_number, str(enrollment.student), "No competency outcomes", "—"])

        summary = []
        for competency in competency_list:
            values = competency_values.get(str(competency.id), [])
            proficient_plus = sum(1 for value in values if value >= LEVEL_ORDER[CompetencyLevel.PROFICIENT])
            summary.append([
                competency.name,
                f"{(proficient_plus / len(values) * 100):.1f}%" if values else "—",
                f"{(sum(values) / len(values)):.2f}/4" if values else "—",
                len(values),
            ])

        distribution_rows = [
            [LEVEL_LABELS[level], f"{distribution[level] / total_levels * 100:.1f}%" if total_levels else "0.0%", str(distribution[level])]
            for level in LEVEL_ORDER
        ]

        return self._build_pdf(classroom, competency_list, summary, distribution_rows, rows, total_levels)

    def _build_pdf(self, classroom, competencies, summary, distribution_rows, rows, total_levels):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title="Competency Outcomes Report",
            author="KEY",
        )
        styles = getSampleStyleSheet()
        title = ParagraphStyle("CompetencyReportTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=4 * mm)
        heading = ParagraphStyle("CompetencyReportHeading", parent=styles["Heading2"], fontSize=11, leading=14, spaceBefore=4 * mm, spaceAfter=2 * mm)
        small = ParagraphStyle("CompetencyReportSmall", parent=styles["BodyText"], fontSize=8, leading=10)

        school_name = classroom.school.name if classroom else "Institution"
        story = [
            Paragraph(school_name, title),
            Paragraph("Competency Outcomes Report", styles["Heading1"]),
            Spacer(1, 2 * mm),
        ]
        if classroom:
            story.append(Table([
                ["Class", classroom.name, "Code", classroom.code, "Stage", classroom.cambridge_stage.name],
                ["Academic Year", classroom.academic_year.name, "Term", f"Term {classroom.term.term_number}", "Competencies", str(len(competencies))],
            ], colWidths=[25 * mm, 55 * mm, 22 * mm, 45 * mm, 22 * mm, 55 * mm], style=TableStyle([
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
            ])), Spacer(1, 4 * mm))

        story.append(Paragraph(f"Level observations: {total_levels}", heading))
        summary_table = Table([["Competency", "Proficient+", "Average Level", "Observations"]] + summary, colWidths=[85 * mm, 35 * mm, 38 * mm, 35 * mm], repeatRows=1)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([summary_table, Paragraph("Level Distribution", heading)])
        distribution_table = Table([["Level", "Share", "Count"]] + distribution_rows, colWidths=[45 * mm, 35 * mm, 35 * mm], repeatRows=1)
        distribution_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([distribution_table, Paragraph("Student Outcomes", heading)])

        outcome_table = Table([["Admission", "Student", "Competency", "Level"]] + rows, colWidths=[32 * mm, 70 * mm, 90 * mm, 40 * mm], repeatRows=1)
        outcome_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([outcome_table, Spacer(1, 6 * mm), Paragraph("This report uses published competency evaluations linked to published assessment results for the selected enrollment scope.", small)])
        doc.build(story)
        buffer.seek(0)
        filename = f"competency-outcomes-{classroom.code if classroom else 'report'}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type="application/pdf")

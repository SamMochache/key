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

from apps.academics.models import Classroom
from apps.assessments.models import Assessment, AssessmentEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.enrollment.models import Enrollment


class AssessmentResultsReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can access assessment reports.")

        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        classroom_id = request.query_params.get("classroom")
        student_id = request.query_params.get("student")
        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")

        classrooms = Classroom.objects.select_related("school", "academic_year", "term", "cambridge_stage")
        classroom = None
        if classroom_id:
            classroom = classrooms.filter(id=classroom_id, is_active=True).first()
            if classroom is None:
                return JsonResponse({"detail": "Classroom not found."}, status=404)
            if school is not None and classroom.school_id != school.id:
                raise PermissionDenied("The classroom does not belong to your institution.")
            if year_id and str(classroom.academic_year_id) != year_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected academic year."}, status=400)
            if term_id and str(classroom.term_id) != term_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected term."}, status=400)

        enrollments = Enrollment.objects.select_related("student", "student__user", "classroom")
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

        if classroom is None and not enrollments.exists():
            return JsonResponse({"detail": "No matching enrolled students were found."}, status=404)

        enrollment_ids = list(enrollments.values_list("id", flat=True))
        if not enrollment_ids:
            return self._build_pdf(
                classroom=classroom,
                assessments=[],
                rows=[],
                summary={"count": 0, "average": None, "highest": None, "lowest": None},
            )

        evaluations = AssessmentEvaluation.objects.filter(
            published=True,
            submission__enrollment_id__in=enrollment_ids,
            submission__assessment__status="PUBLISHED",
        ).select_related(
            "submission__assessment",
            "submission__enrollment__student",
        ).order_by("submission__enrollment__student__admission_number", "submission__assessment__title")

        if classroom is not None:
            evaluations = evaluations.filter(submission__assessment__lesson_session__timetable_entry__teacher_subject__classroom=classroom)

        assessment_ids = list(evaluations.values_list("submission__assessment_id", flat=True).distinct())
        assessments = list(
            Assessment.objects.filter(id__in=assessment_ids)
            .select_related("lesson_session")
            .order_by("title")
        )

        result_map = {}
        all_scores = []
        for evaluation in evaluations:
            percentage = float(evaluation.percentage) if evaluation.percentage is not None else None
            key = (str(evaluation.submission.enrollment_id), str(evaluation.submission.assessment_id))
            result_map[key] = percentage
            if percentage is not None:
                all_scores.append(percentage)

        rows = []
        for enrollment in enrollments:
            scores = [
                result_map[(str(enrollment.id), str(assessment.id))]
                for assessment in assessments
                if (str(enrollment.id), str(assessment.id)) in result_map
                and result_map[(str(enrollment.id), str(assessment.id))] is not None
            ]
            average = sum(scores) / len(scores) if scores else None
            for assessment in assessments:
                value = result_map.get((str(enrollment.id), str(assessment.id)))
                rows.append([
                    enrollment.student.admission_number,
                    str(enrollment.student),
                    assessment.title,
                    assessment.get_assessment_type_display(),
                    f"{value:.1f}%" if value is not None else "—",
                ])
            if not assessments:
                rows.append([enrollment.student.admission_number, str(enrollment.student), "No published results", "—", "—"])

        summary = {
            "count": len(all_scores),
            "average": sum(all_scores) / len(all_scores) if all_scores else None,
            "highest": max(all_scores) if all_scores else None,
            "lowest": min(all_scores) if all_scores else None,
        }
        return self._build_pdf(classroom, assessments, rows, summary)

    def _build_pdf(self, classroom, assessments, rows, summary):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title="Assessment Results Report",
            author="KEY",
        )
        styles = getSampleStyleSheet()
        title = ParagraphStyle("AssessmentReportTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=4 * mm)
        heading = ParagraphStyle("AssessmentReportHeading", parent=styles["Heading2"], fontSize=11, leading=14, spaceBefore=4 * mm, spaceAfter=2 * mm)
        small = ParagraphStyle("AssessmentReportSmall", parent=styles["BodyText"], fontSize=8, leading=10)

        school_name = classroom.school.name if classroom else "Institution"
        story = [
            Paragraph(school_name, title),
            Paragraph("Assessment Results Report", styles["Heading1"]),
            Spacer(1, 2 * mm),
        ]
        if classroom:
            info = [
                ["Class", classroom.name, "Code", classroom.code, "Stage", classroom.cambridge_stage.name],
                ["Academic Year", classroom.academic_year.name, "Term", f"Term {classroom.term.term_number}", "Assessments", str(len(assessments))],
            ]
            info_table = Table(info, colWidths=[25 * mm, 55 * mm, 22 * mm, 45 * mm, 22 * mm, 55 * mm])
            info_table.setStyle(TableStyle([
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

        def pct(value):
            return f"{value:.1f}%" if value is not None else "—"

        summary_table = Table([["Published Results", str(summary["count"]), "Average", pct(summary["average"]), "Highest", pct(summary["highest"]), "Lowest", pct(summary["lowest"])]] , colWidths=[31 * mm, 27 * mm, 25 * mm, 27 * mm, 25 * mm, 27 * mm, 25 * mm, 27 * mm])
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
        story.extend([summary_table, Paragraph("Student Results", heading)])

        table_data = [["Admission", "Student", "Assessment", "Type", "Percentage"]] + rows
        if len(table_data) == 1:
            table_data.append(["—", "No published assessment results", "—", "—", "—"])
        result_table = Table(table_data, colWidths=[32 * mm, 70 * mm, 75 * mm, 45 * mm, 30 * mm], repeatRows=1)
        result_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([
            result_table,
            Spacer(1, 6 * mm),
            Paragraph("This report contains published assessment evaluations available in KEY for the selected scope. Percentages are based on the published evaluation percentage.", small),
        ])
        doc.build(story)
        buffer.seek(0)
        filename = f"assessment-results-{classroom.code if classroom else 'report'}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type="application/pdf")

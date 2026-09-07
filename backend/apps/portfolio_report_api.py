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
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.enrollment.models import Enrollment
from apps.portfolio.models import Artifact, PortfolioItem


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
            classroom = Classroom.objects.select_related("school", "academic_year", "term", "cambridge_stage").filter(id=classroom_id, is_active=True).first()
            if classroom is None:
                return JsonResponse({"detail": "Classroom not found."}, status=404)
            if school is not None and classroom.school_id != school.id:
                raise PermissionDenied("The classroom does not belong to your institution.")
            if year_id and str(classroom.academic_year_id) != year_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected academic year."}, status=400)
            if term_id and str(classroom.term_id) != term_id:
                return JsonResponse({"detail": "The classroom does not belong to the selected term."}, status=400)

        enrollments = Enrollment.objects.select_related("student", "classroom").filter(status__in=["ACTIVE", "COMPLETED"])
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
        items = PortfolioItem.objects.filter(
            portfolio__student_id__in=enrollments.values_list("student_id", flat=True),
        ).select_related(
            "portfolio__student__user",
            "assessment_submission__assessment",
            "lesson_session",
        ).prefetch_related("artifacts")

        if year_id:
            items = items.filter(
                event_date__gte=classroom.academic_year.start_date if classroom else "1900-01-01",
                event_date__lte=classroom.academic_year.end_date if classroom else "2999-12-31",
            )
        if classroom is not None:
            items = items.filter(portfolio__student__enrollments__classroom=classroom)

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
                artifact_count += item.artifacts.count()
                if item.assessment_submission_id and item.assessment_submission_id in evaluation_ids:
                    published_assessment_ids.add(item.assessment_submission_id)
                if item.lesson_session_id:
                    lesson_ids.add(item.lesson_session_id)
                total_assessments.update(published_assessment_ids)
                total_lessons.update(lesson_ids)
                item_rows.append([
                    enrollment.student.admission_number,
                    str(enrollment.student),
                    item.title,
                    item.get_item_type_display(),
                    item.event_date.strftime("%d %b %Y"),
                    str(item.artifacts.count()),
                ])
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
        return self._build_pdf(classroom, summary, rows, item_rows)

    def _build_pdf(self, classroom, summary, rows, item_rows):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
            title="Portfolio & Evidence Summary",
            author="KEY",
        )
        styles = getSampleStyleSheet()
        title = ParagraphStyle("PortfolioReportTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=4 * mm)
        heading = ParagraphStyle("PortfolioReportHeading", parent=styles["Heading2"], fontSize=11, leading=14, spaceBefore=4 * mm, spaceAfter=2 * mm)
        small = ParagraphStyle("PortfolioReportSmall", parent=styles["BodyText"], fontSize=7.5, leading=9)

        school_name = classroom.school.name if classroom else "Institution"
        story = [Paragraph(school_name, title), Paragraph("Portfolio & Evidence Summary", styles["Heading1"])]
        if classroom:
            info = [["Class", classroom.name, "Code", classroom.code, "Stage", classroom.cambridge_stage.name], ["Academic Year", classroom.academic_year.name, "Term", f"Term {classroom.term.term_number}", "Students", str(summary["students"])]]
            info_table = Table(info, colWidths=[25*mm, 55*mm, 22*mm, 45*mm, 22*mm, 55*mm])
            info_table.setStyle(TableStyle([("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTNAME",(4,0),(4,-1),"Helvetica-Bold"),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#f1f5f9")),("BACKGROUND",(2,0),(2,-1),colors.HexColor("#f1f5f9")),("BACKGROUND",(4,0),(4,-1),colors.HexColor("#f1f5f9")),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#cbd5e1")),("FONTSIZE",(0,0),(-1,-1),8.5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
            story.extend([info_table, Spacer(1, 4*mm)])

        summary_table = Table([["Students", str(summary["students"]), "Portfolio Items", str(summary["items"]), "Artifacts", str(summary["artifacts"]), "Assessments", str(summary["assessments"]), "Lessons", str(summary["lessons"])]], colWidths=[25*mm,22*mm,32*mm,22*mm,24*mm,22*mm,27*mm,22*mm,20*mm,22*mm])
        summary_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f8fafc")),("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#cbd5e1")),("INNERGRID",(0,0),(-1,-1),0.3,colors.HexColor("#e2e8f0")),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("ALIGN",(0,0),(-1,-1),"CENTER"),("FONTSIZE",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.extend([summary_table, Paragraph("Student Portfolio Summary", heading)])

        student_table = Table([["Admission", "Student", "Items", "Artifacts", "Published Assessments", "Lessons"]] + rows, colWidths=[30*mm,70*mm,22*mm,25*mm,40*mm,25*mm], repeatRows=1)
        student_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e2e8f0")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#cbd5e1")),("FONTSIZE",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.extend([student_table, Paragraph("Portfolio Evidence", heading)])

        evidence_table = Table([["Admission", "Student", "Portfolio Item", "Type", "Date", "Artifacts"]] + item_rows, colWidths=[28*mm,60*mm,80*mm,35*mm,30*mm,25*mm], repeatRows=1)
        evidence_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e2e8f0")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cbd5e1")),("FONTSIZE",(0,0),(-1,-1),7.5),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.extend([evidence_table, Spacer(1, 5*mm), Paragraph("This report summarizes portfolio items and attached evidence within the selected enrollment scope. Published assessment references are counted only when a published evaluation exists.", small)])
        doc.build(story)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"portfolio-evidence-{classroom.code if classroom else 'report'}.pdf", content_type="application/pdf")

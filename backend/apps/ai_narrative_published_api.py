from io import BytesIO

from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.assessments.models import AINarrativeReport
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.enrollment.models import Enrollment
from apps.reporting.pdf import build_document, data_table, report_header, report_styles, summary_table
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer


class PublishedAINarrativeReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        reports = AINarrativeReport.objects.select_related("student__user", "academic_year", "term")

        if role == UserRole.STUDENT:
            reports = reports.filter(student_id=request.user.student_profile.id, status=AINarrativeReport.Status.PUBLISHED)
        elif role in {UserRole.ADMIN, UserRole.TEACHER}:
            school = get_user_school(request.user)
            if school is not None:
                reports = reports.filter(
                    student__school_id=school.id,
                    status=AINarrativeReport.Status.PUBLISHED,
                )
            else:
                reports = reports.filter(status=AINarrativeReport.Status.PUBLISHED)
        else:
            raise PermissionDenied("Only students and staff can access published AI reports.")

        if request.query_params.get("academic_year"):
            reports = reports.filter(academic_year_id=request.query_params["academic_year"])
        if request.query_params.get("term"):
            reports = reports.filter(term_id=request.query_params["term"])
        if request.query_params.get("student") and role != UserRole.STUDENT:
            reports = reports.filter(student_id=request.query_params["student"])

        results = []
        for report in reports[:50]:
            narrative = report.edited_content or report.generated_content
            results.append({
                "id": str(report.id),
                "student": str(report.student_id),
                "student_name": report.student.user.get_full_name() or report.student.admission_number,
                "academic_year": str(report.academic_year_id),
                "academic_year_name": report.academic_year.name,
                "term": str(report.term_id),
                "term_number": report.term.term_number,
                "narrative": narrative,
                "facts": report.source_data_snapshot,
                "published_at": report.published_at,
            })
        return JsonResponse({"results": results})


def _published_report_for_user(request, report_id):
    report = AINarrativeReport.objects.select_related(
        "student__user", "academic_year", "term", "published_by"
    ).filter(id=report_id, status=AINarrativeReport.Status.PUBLISHED).first()
    if report is None:
        return None

    role = get_user_role(request.user)
    if role == UserRole.STUDENT:
        if report.student_id != request.user.student_profile.id:
            raise PermissionDenied("You can only access your own published report.")
        return report

    if role in {UserRole.ADMIN, UserRole.TEACHER}:
        school = get_user_school(request.user)
        if school is not None and report.student.school_id != school.id:
            raise PermissionDenied("The report does not belong to your institution.")
        return report

    raise PermissionDenied("You do not have access to published AI reports.")


class PublishedAINarrativeReportPdfView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, report_id):
        report = _published_report_for_user(request, report_id)
        if report is None:
            return JsonResponse({"detail": "Published report not found."}, status=404)

        enrollment = Enrollment.objects.select_related(
            "classroom", "classroom__school", "classroom__cambridge_stage"
        ).filter(
            student_id=report.student_id,
            academic_year_id=report.academic_year_id,
            term_id=report.term_id,
            status__in=["ACTIVE", "COMPLETED"],
        ).first()
        if enrollment is None:
            return JsonResponse({"detail": "The report's enrollment could not be resolved."}, status=404)

        narrative = report.edited_content or report.generated_content
        facts = report.source_data_snapshot or {}
        learner = facts.get("learner", {})
        assessment = facts.get("assessment", {})
        attendance = facts.get("attendance", {})
        portfolio = facts.get("portfolio", {})
        competencies = facts.get("competencies", [])
        styles = report_styles()

        buffer = BytesIO()
        document = build_document(buffer, title="KEY AI Learning Progress Report")
        story = []
        school_name = enrollment.classroom.school.name
        report_header(
            story,
            school_name,
            "AI Learning Progress Report",
            f"{report.academic_year.name} · Term {report.term.term_number} · Teacher-reviewed and published",
        )

        story.append(summary_table([
            f"Learner\n{learner.get('first_name') or report.student.user.first_name}",
            f"Admission\n{report.student.admission_number}",
            f"Class\n{enrollment.classroom.name}",
            f"Assessment\n{assessment.get('average_percentage') if assessment.get('average_percentage') is not None else '—'}%",
            f"Attendance\n{attendance.get('attendance_percentage') if attendance.get('attendance_percentage') is not None else '—'}%",
        ], [38 * mm, 34 * mm, 42 * mm, 38 * mm, 38 * mm]))
        story.append(Spacer(1, 4 * mm))

        sections = [
            ("Overall Progress", narrative.get("summary", "")),
            ("Strengths", narrative.get("strengths", "")),
            ("Areas for Development", narrative.get("development_areas", "")),
            ("Suggested Next Steps", narrative.get("next_steps", "")),
            ("Teacher Review Note", narrative.get("teacher_note", "")),
        ]
        for title, text in sections:
            story.append(Paragraph(title, styles["heading"]))
            story.append(Paragraph(text, styles["body"]))

        if competencies:
            story.append(Paragraph("Competency Evidence", styles["heading"]))
            rows = [[
                Paragraph("Competency", styles["table_header"]),
                Paragraph("Observations", styles["table_header"]),
                Paragraph("Highest Level", styles["table_header"]),
                Paragraph("Average", styles["table_header"]),
            ]]
            for item in competencies:
                rows.append([
                    Paragraph(str(item.get("name", "")), styles["table"]),
                    Paragraph(str(item.get("observations", 0)), styles["table"]),
                    Paragraph(str(item.get("highest_level", "Not recorded")), styles["table"]),
                    Paragraph(str(item.get("average_level") if item.get("average_level") is not None else "—"), styles["table"]),
                ])
            story.append(data_table(rows, [78 * mm, 32 * mm, 52 * mm, 38 * mm], center_from=1))

        story.append(Paragraph("Evidence Snapshot", styles["heading"]))
        story.append(Paragraph(
            f"Published assessment results: {assessment.get('published_results', 0)} · "
            f"Portfolio items: {portfolio.get('items', 0)} · "
            f"Artifacts: {portfolio.get('artifacts', 0)}.",
            styles["body"],
        ))
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(
            "This is the official published narrative for the selected academic period. "
            "It was generated from KEY records, reviewed by an authorized staff member, and is not regenerated when this PDF is downloaded.",
            styles["small"],
        ))

        document.build(story, onFirstPage=lambda c, d: __import__("apps.reporting.pdf", fromlist=["footer"]).footer(c, d), onLaterPages=lambda c, d: __import__("apps.reporting.pdf", fromlist=["footer"]).footer(c, d))
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        safe_name = report.student.user.get_full_name().strip().replace(" ", "-") or report.student.admission_number
        response["Content-Disposition"] = f'attachment; filename="KEY-AI-Report-{safe_name}-Term-{report.term.term_number}.pdf"'
        return response

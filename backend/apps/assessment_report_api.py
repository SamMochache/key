from io import BytesIO

from django.http import FileResponse, JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.academics.models import Classroom
from apps.assessments.models import Assessment, AssessmentEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.enrollment.models import Enrollment
from apps.reporting.pdf import build_document, data_table, footer, info_table, report_header, report_styles, summary_table


class AssessmentResultsReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can access assessment reports.")
        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")
        classroom_id, student_id = request.query_params.get("classroom"), request.query_params.get("student")
        year_id, term_id = request.query_params.get("academic_year"), request.query_params.get("term")
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
            return self._build_pdf(classroom, [], [], {"count": 0, "average": None, "highest": None, "lowest": None})
        evaluations = AssessmentEvaluation.objects.filter(published=True, submission__enrollment_id__in=enrollment_ids, submission__assessment__status="PUBLISHED").select_related("submission__assessment", "submission__enrollment__student").order_by("submission__enrollment__student__admission_number", "submission__assessment__title")
        if classroom is not None:
            evaluations = evaluations.filter(submission__assessment__lesson_session__timetable_entry__teacher_subject__classroom=classroom)
        assessment_ids = list(evaluations.values_list("submission__assessment_id", flat=True).distinct())
        assessments = list(Assessment.objects.filter(id__in=assessment_ids).select_related("lesson_session").order_by("title"))
        result_map, all_scores = {}, []
        for evaluation in evaluations:
            percentage = float(evaluation.percentage) if evaluation.percentage is not None else None
            result_map[(str(evaluation.submission.enrollment_id), str(evaluation.submission.assessment_id))] = percentage
            if percentage is not None:
                all_scores.append(percentage)
        rows = []
        for enrollment in enrollments:
            for assessment in assessments:
                value = result_map.get((str(enrollment.id), str(assessment.id)))
                rows.append([enrollment.student.admission_number, str(enrollment.student), assessment.title, assessment.get_assessment_type_display(), f"{value:.1f}%" if value is not None else "—"])
            if not assessments:
                rows.append([enrollment.student.admission_number, str(enrollment.student), "No published results", "—", "—"])
        summary = {"count": len(all_scores), "average": sum(all_scores) / len(all_scores) if all_scores else None, "highest": max(all_scores) if all_scores else None, "lowest": min(all_scores) if all_scores else None}
        return self._build_pdf(classroom, assessments, rows, summary)

    def _build_pdf(self, classroom, assessments, rows, summary):
        buffer = BytesIO()
        doc = build_document(buffer, landscape_mode=True, title="Assessment Results Report")
        styles = report_styles()
        story = []
        school_name = classroom.school.name if classroom else "Institution"
        subtitle = f"{classroom.academic_year.name} • Term {classroom.term.term_number}" if classroom else "Published assessment results"
        report_header(story, school_name, "Assessment Results Report", subtitle)
        if classroom:
            story.append(info_table([["Class", classroom.name, "Code", classroom.code, "Stage", classroom.cambridge_stage.name], ["Academic Year", classroom.academic_year.name, "Term", f"Term {classroom.term.term_number}", "Assessments", str(len(assessments))]], [25 * mm, 55 * mm, 22 * mm, 45 * mm, 22 * mm, 55 * mm]))
            story.append(Spacer(1, 4 * mm))
        def pct(value): return f"{value:.1f}%" if value is not None else "—"
        story.append(summary_table([["Published Results", str(summary["count"]), "Average", pct(summary["average"]), "Highest", pct(summary["highest"]), "Lowest", pct(summary["lowest"])]], [31 * mm, 27 * mm, 25 * mm, 27 * mm, 25 * mm, 27 * mm, 25 * mm, 27 * mm]))
        story.append(Paragraph("Student Results", styles["heading"]))
        table_data = [["Admission", "Student", "Assessment", "Type", "Percentage"]] + rows
        if len(table_data) == 1:
            table_data.append(["—", "No published assessment results", "—", "—", "—"])
        story.extend([data_table(table_data, [32 * mm, 70 * mm, 75 * mm, 45 * mm, 30 * mm], center_from=4), Spacer(1, 6 * mm), Paragraph("This report contains published assessment evaluations available in KEY for the selected scope. Percentages are based on the published evaluation percentage.", styles["small"])])
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"assessment-results-{classroom.code if classroom else 'report'}.pdf", content_type="application/pdf")

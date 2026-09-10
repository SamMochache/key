from io import BytesIO

from django.db.models import Avg
from django.http import FileResponse, JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from reportlab.lib.units import mm
from reportlab.platypus import Spacer, Paragraph

from apps.academics.models import AcademicYear, Term
from apps.assessments.models import AssessmentEvaluation, AssessmentSubmission, CompetencyEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.parents.models import ParentStudentRelationship
from apps.students.models import Student
from apps.reporting.pdf import build_document, data_table, footer, info_table, report_header, report_styles, summary_table

COMPETENCY_LABELS = {"BEGINNING": "Beginning", "DEVELOPING": "Developing", "PROFICIENT": "Proficient", "ADVANCED": "Advanced"}


class StudentReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT, UserRole.PARENT}:
            raise PermissionDenied("Your account does not have report access.")
        school = get_user_school(request.user)
        if school is None and role not in {UserRole.ADMIN, UserRole.PARENT}:
            raise PermissionDenied("Your account is not associated with an institution.")

        student_id = request.query_params.get("student")
        if role == UserRole.STUDENT:
            student = Student.objects.filter(user=request.user, is_active=True).first()
            if student_id and (student is None or str(student.id) != student_id):
                raise PermissionDenied("Students may only access their own report.")
        elif role == UserRole.PARENT:
            if not student_id:
                return JsonResponse({"detail": "Select one of your linked learners."}, status=400)
            relationship = ParentStudentRelationship.objects.select_related("student", "student__school").filter(
                parent__user=request.user,
                parent__is_active=True,
                student_id=student_id,
                student__is_active=True,
                is_active=True,
                can_view_reports=True,
            ).first()
            if relationship is None:
                raise PermissionDenied("You do not have report access for this learner.")
            student = relationship.student
        else:
            student = Student.objects.filter(id=student_id, is_active=True).first()

        if student is None:
            return JsonResponse({"detail": "A valid student is required."}, status=400)
        if school is not None and student.school_id != school.id:
            raise PermissionDenied("The student does not belong to your institution.")

        year_id = request.query_params.get("academic_year")
        term_id = request.query_params.get("term")
        enrollments = Enrollment.objects.filter(student=student).select_related("classroom", "academic_year", "term")
        if year_id:
            enrollments = enrollments.filter(academic_year_id=year_id)
        if term_id:
            enrollments = enrollments.filter(term_id=term_id)
        enrollment = enrollments.order_by("-term__start_date").first()
        if enrollment is None:
            return JsonResponse({"detail": "No enrollment found for the selected period."}, status=404)

        enrollment_ids = Enrollment.objects.filter(student=student, academic_year=enrollment.academic_year, term=enrollment.term).values_list("id", flat=True)
        submissions = AssessmentSubmission.objects.filter(enrollment_id__in=enrollment_ids, assessment__lesson_session__timetable_entry__timetable__term=enrollment.term, evaluation__published=True).select_related("assessment", "evaluation", "assessment__lesson_session__timetable_entry__teacher_subject__subject").order_by("assessment__lesson_session__lesson_date")
        attendance = AttendanceRecord.objects.filter(enrollment_id__in=enrollment_ids)
        total_attendance = attendance.count()
        present = attendance.filter(status__in=["PRESENT", "LATE"]).count()
        attendance_rate = round((present / total_attendance) * 100, 1) if total_attendance else None
        scores = [float(value) for value in submissions.values_list("evaluation__percentage", flat=True) if value is not None]
        overall_average = round(sum(scores) / len(scores), 1) if scores else None
        competencies = CompetencyEvaluation.objects.filter(evaluation__submission__enrollment_id__in=enrollment_ids, evaluation__published=True).select_related("competency")
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
        doc = build_document(buffer, title=f"Student Academic Report - {student}")
        styles = report_styles()
        story = []
        report_header(story, student.school.name, "Student Academic Progress Report", f"{enrollment.academic_year.name} • Term {enrollment.term.term_number}")
        story.append(info_table([
            ["Student", str(student), "Admission", student.admission_number],
            ["Institution", student.school.name, "Class", enrollment.classroom.name],
            ["Academic Year", enrollment.academic_year.name, "Term", f"Term {enrollment.term.term_number}"],
        ], [28 * mm, 67 * mm, 28 * mm, 57 * mm]))
        story.append(Spacer(1, 5 * mm))
        story.append(summary_table(["Overall Average", f"{overall_average:.1f}%" if overall_average is not None else "—", "Attendance", f"{attendance_rate:.1f}%" if attendance_rate is not None else "—", "Assessments", str(len(submissions))], [31 * mm, 27 * mm, 25 * mm, 27 * mm, 28 * mm, 42 * mm]))
        story.append(Paragraph("Assessment Results", styles["heading"]))
        result_data = [["Assessment", "Subject", "Date", "Score"]]
        for submission in submissions:
            subject = submission.assessment.lesson_session.timetable_entry.teacher_subject.subject.name
            percentage = submission.evaluation.percentage
            result_data.append([submission.assessment.title, subject, submission.assessment.lesson_session.lesson_date.strftime("%d %b %Y"), f"{float(percentage):.1f}%" if percentage is not None else "—"])
        if len(result_data) == 1:
            result_data.append(["No published assessment results", "—", "—", "—"])
        story.append(data_table(result_data, [62 * mm, 43 * mm, 35 * mm, 20 * mm], center_from=3))
        story.append(Paragraph("Competency Outcomes", styles["heading"]))
        competency_data_table = [["Competency", "Reported Level"]] + [list(row) for row in competency_rows]
        if len(competency_data_table) == 1:
            competency_data_table.append(["No competency evaluations recorded", "—"])
        story.append(data_table(competency_data_table, [125 * mm, 35 * mm]))
        story.extend([Spacer(1, 8 * mm), Paragraph("This report contains published academic, attendance, and competency records available in KEY for the selected academic period.", styles["small"])])
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"student-report-{student.admission_number}-{enrollment.academic_year.name}-term-{enrollment.term.term_number}.pdf", content_type="application/pdf")

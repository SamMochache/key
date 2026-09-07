from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.assessments.models import AssessmentEvaluation, AssessmentSubmission, CompetencyEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.academics.models import Classroom


class AnalyticsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT}:
            raise PermissionDenied("Your account does not have analytics access.")

        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

        students = Student.objects.filter(is_active=True)
        enrollments = Enrollment.objects.all()
        attendance = AttendanceRecord.objects.all()
        submissions = AssessmentSubmission.objects.all()
        evaluations = AssessmentEvaluation.objects.filter(published=True)
        competencies = CompetencyEvaluation.objects.filter(evaluation__published=True)
        classrooms = Classroom.objects.filter(is_active=True)

        if role == UserRole.STUDENT:
            students = students.filter(user=request.user)
            enrollments = enrollments.filter(student__user=request.user)
            attendance = attendance.filter(enrollment__student__user=request.user)
            submissions = submissions.filter(enrollment__student__user=request.user)
            evaluations = evaluations.filter(submission__enrollment__student__user=request.user)
            competencies = competencies.filter(evaluation__submission__enrollment__student__user=request.user)
            classrooms = classrooms.filter(enrollments__student__user=request.user).distinct()
        elif school is not None:
            students = students.filter(school=school)
            enrollments = enrollments.filter(student__school=school)
            attendance = attendance.filter(enrollment__student__school=school)
            submissions = submissions.filter(enrollment__student__school=school)
            evaluations = evaluations.filter(submission__enrollment__student__school=school)
            competencies = competencies.filter(evaluation__submission__enrollment__student__school=school)
            classrooms = classrooms.filter(school=school)

        total_attendance = attendance.count()
        present_count = attendance.filter(status="PRESENT").count()
        late_count = attendance.filter(status="LATE").count()
        attendance_rate = ((present_count + late_count) / total_attendance * 100) if total_attendance else None

        evaluated_scores = list(evaluations.values_list("percentage", flat=True))
        evaluated_scores = [float(score) for score in evaluated_scores if score is not None]
        growth_index = round(sum(evaluated_scores) / len(evaluated_scores), 1) if evaluated_scores else None

        submitted = submissions.count()
        graded = submissions.filter(status="GRADED").count()
        completion_rate = (submitted / (submitted + submissions.filter(status="DRAFT").count()) * 100) if submitted else None

        competency_values = list(competencies.values_list("score", flat=True))
        competency_values = [float(value) for value in competency_values if value is not None]
        outcomes_secure = (
            round(sum(1 for value in competency_values if value >= 3) / len(competency_values) * 100, 1)
            if competency_values else None
        )

        monthly_attendance = []
        for offset in range(5, -1, -1):
            month_start = (timezone.localdate().replace(day=1) - timezone.timedelta(days=offset * 28)).replace(day=1)
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            records = attendance.filter(attendance_register__lesson_session__lesson_date__gte=month_start, attendance_register__lesson_session__lesson_date__lt=next_month)
            total = records.count()
            present = records.filter(status__in=["PRESENT", "LATE"]).count()
            monthly_attendance.append({"month": month_start.strftime("%b"), "rate": round(present / total * 100, 1) if total else 0})

        classroom_rows = []
        for classroom in classrooms.order_by("name")[:12]:
            class_attendance = attendance.filter(enrollment__classroom=classroom)
            class_total = class_attendance.count()
            class_present = class_attendance.filter(status__in=["PRESENT", "LATE"]).count()
            class_evals = evaluations.filter(submission__enrollment__classroom=classroom).values_list("percentage", flat=True)
            class_scores = [float(value) for value in class_evals if value is not None]
            classroom_rows.append({
                "name": classroom.name,
                "growth": round(sum(class_scores) / len(class_scores), 1) if class_scores else 0,
                "attendance": round(class_present / class_total * 100, 1) if class_total else 0,
            })

        competency_rows = []
        for row in competencies.values("competency__name").annotate(value=Avg("score")).order_by("competency__sequence")[:8]:
            competency_rows.append({"skill": row["competency__name"], "value": round(float(row["value"] or 0) / 5 * 100, 1)})

        return Response({
            "summary": {
                "growth_index": growth_index,
                "attendance_rate": round(attendance_rate, 1) if attendance_rate is not None else None,
                "assignment_completion": round(completion_rate, 1) if completion_rate is not None else None,
                "outcomes_secure": outcomes_secure,
                "students": students.count(),
                "enrollments": enrollments.count(),
                "graded_submissions": graded,
            },
            "attendance_trend": monthly_attendance,
            "growth_trend": [],
            "class_compare": classroom_rows,
            "competency_radar": competency_rows,
        })

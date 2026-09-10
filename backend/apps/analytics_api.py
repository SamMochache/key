from datetime import timedelta

from django.db.models import Avg, Count, DecimalField, OuterRef, Q, Subquery
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.academics.models import Classroom
from apps.assessments.models import AssessmentEvaluation, AssessmentSubmission, CompetencyEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.students.models import Student


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
        elif role == UserRole.TEACHER:
            teacher = getattr(request.user, "teacher_profile", None)
            if teacher is None:
                raise PermissionDenied("Teacher profile not found.")
            assigned_enrollments = Enrollment.objects.filter(
                classroom__teacher_assignments__teacher_id=teacher.id,
                classroom__teacher_assignments__is_active=True,
            ).distinct()
            students = students.filter(enrollments__in=assigned_enrollments).distinct()
            enrollments = enrollments.filter(id__in=assigned_enrollments.values("id"))
            attendance = attendance.filter(enrollment_id__in=assigned_enrollments.values("id"))
            submissions = submissions.filter(enrollment_id__in=assigned_enrollments.values("id"))
            evaluations = evaluations.filter(submission__enrollment_id__in=assigned_enrollments.values("id"))
            competencies = competencies.filter(evaluation__submission__enrollment_id__in=assigned_enrollments.values("id"))
            classrooms = classrooms.filter(
                teacher_assignments__teacher_id=teacher.id,
                teacher_assignments__is_active=True,
            ).distinct()
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

        evaluated_scores = [float(score) for score in evaluations.values_list("percentage", flat=True) if score is not None]
        growth_index = round(sum(evaluated_scores) / len(evaluated_scores), 1) if evaluated_scores else None

        submission_total = submissions.count()
        graded = submissions.filter(status="GRADED").count()
        completion_rate = (graded / submission_total * 100) if submission_total else None

        competency_scale = {
            "BEGINNING": 1,
            "DEVELOPING": 2,
            "PROFICIENT": 3,
            "ADVANCED": 4,
        }
        competency_values = [
            competency_scale[level]
            for level in competencies.values_list("level", flat=True)
            if level in competency_scale
        ]
        outcomes_secure = (
            round(sum(1 for value in competency_values if value >= 3) / len(competency_values) * 100, 1)
            if competency_values else None
        )

        today = timezone.localdate()
        monthly_rows = attendance.values(
            month=TruncMonth("attendance_register__lesson_session__lesson_date")
        ).annotate(
            total=Count("id"),
            present=Count("id", filter=Q(status__in=["PRESENT", "LATE"])),
        ).order_by("month")
        monthly_map = {
            row["month"].strftime("%Y-%m"): row
            for row in monthly_rows
            if row["month"] is not None
        }

        monthly_attendance = []
        for offset in range(5, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=offset * 28)).replace(day=1)
            row = monthly_map.get(month_start.strftime("%Y-%m"))
            total = row["total"] if row else 0
            present = row["present"] if row else 0
            monthly_attendance.append({
                "month": month_start.strftime("%b"),
                "rate": round(present / total * 100, 1) if total else 0,
            })

        growth_trend = []
        term_groups = evaluations.values(
            "submission__assessment__lesson_session__timetable_entry__timetable__term__term_number"
        ).annotate(value=Avg("percentage")).order_by(
            "submission__assessment__lesson_session__timetable_entry__timetable__term__term_number"
        )
        for row in term_groups:
            term_number = row["submission__assessment__lesson_session__timetable_entry__timetable__term__term_number"]
            if term_number is not None:
                value = round(float(row["value"] or 0), 1)
                growth_trend.append({"term": f"Term {term_number}", "practical": value, "language": value, "math": value, "culture": value})

        class_growth = evaluations.filter(
            submission__enrollment__classroom=OuterRef("pk")
        ).values("submission__enrollment__classroom").annotate(
            value=Avg("percentage")
        ).values("value")[:1]
        classroom_rows = []
        for classroom in classrooms.order_by("name").annotate(
            attendance_total=Count("enrollments__attendance_records", distinct=True),
            attendance_present=Count(
                "enrollments__attendance_records",
                filter=Q(enrollments__attendance_records__status__in=["PRESENT", "LATE"]),
                distinct=True,
            ),
            growth=Subquery(
                class_growth,
                output_field=DecimalField(max_digits=5, decimal_places=2),
            ),
        )[:12]:
            total = classroom.attendance_total
            present = classroom.attendance_present
            classroom_rows.append({
                "name": classroom.name,
                "growth": round(float(classroom.growth or 0), 1),
                "attendance": round(present / total * 100, 1) if total else 0,
            })

        competency_rows = []
        competency_groups = competencies.values(
            "competency__name",
            "competency__sequence",
            "level",
        ).order_by("competency__sequence")
        grouped_levels = {}
        for row in competency_groups:
            key = (row["competency__name"], row["competency__sequence"])
            grouped_levels.setdefault(key, []).append(row["level"])

        for (name, sequence), levels in sorted(grouped_levels.items(), key=lambda item: item[0][1])[:8]:
            numeric_levels = [competency_scale[level] for level in levels if level in competency_scale]
            average_level = sum(numeric_levels) / len(numeric_levels) if numeric_levels else 0
            competency_rows.append({"skill": name, "value": round(average_level / 4 * 100, 1)})

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
            "growth_trend": growth_trend,
            "class_compare": classroom_rows,
            "competency_radar": competency_rows,
        })

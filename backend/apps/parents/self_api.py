from datetime import date

from django.db.models import Prefetch
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.assessments.models import AssessmentSubmission
from apps.assessments.permissions import UserRole, get_user_role
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.portfolio.models import PortfolioItem

from .models import ParentStudentRelationship


def student_age(date_of_birth):
    today = date.today()
    birthday = (today.month, today.day)
    born_birthday = (date_of_birth.month, date_of_birth.day)
    return today.year - date_of_birth.year - int(birthday < born_birthday)


class ParentChildrenView(views.APIView):
    """Return only the learners linked to the authenticated parent."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if get_user_role(request.user) != UserRole.PARENT:
            raise PermissionDenied("Only parent accounts can access linked learners.")

        # Prefetch the learner's related data in bounded queries instead of
        # issuing several database queries for every linked child.
        enrollment_qs = Enrollment.objects.select_related(
            "classroom", "academic_year", "term"
        ).prefetch_related(
            Prefetch(
                "attendance_records",
                queryset=AttendanceRecord.objects.only("id", "enrollment_id", "status"),
                to_attr="prefetched_attendance_records",
            ),
            Prefetch(
                "assessment_submissions",
                queryset=AssessmentSubmission.objects.filter(
                    evaluation__published=True,
                    evaluation__percentage__isnull=False,
                ).select_related("evaluation").only(
                    "id", "enrollment_id", "evaluation__id", "evaluation__percentage"
                ),
                to_attr="prefetched_submissions",
            ),
        ).order_by("-academic_year__start_date", "-term__term_number")

        portfolio_qs = PortfolioItem.objects.order_by("-event_date", "-created_at")
        relationships = (
            ParentStudentRelationship.objects.filter(
                parent__user=request.user,
                parent__is_active=True,
                is_active=True,
                student__is_active=True,
            )
            .select_related("student__user", "student__school")
            .prefetch_related(
                Prefetch("student__enrollments", queryset=enrollment_qs, to_attr="prefetched_enrollments"),
                Prefetch("student__portfolio__items", queryset=portfolio_qs, to_attr="prefetched_portfolio_items"),
            )
        )

        results = []
        for relationship in relationships:
            student = relationship.student
            enrollments = getattr(student, "prefetched_enrollments", [])
            enrollment = enrollments[0] if enrollments else None

            attendance_total = 0
            attendance_present = 0
            percentages = []
            for child_enrollment in enrollments:
                records = getattr(child_enrollment, "prefetched_attendance_records", [])
                attendance_total += len(records)
                attendance_present += sum(
                    1 for record in records if record.status in {"PRESENT", "LATE"}
                )
                percentages.extend(
                    float(submission.evaluation.percentage)
                    for submission in getattr(child_enrollment, "prefetched_submissions", [])
                    if getattr(submission, "evaluation", None) is not None
                    and submission.evaluation.percentage is not None
                )

            attendance_rate = round(attendance_present * 100 / attendance_total, 1) if attendance_total else None
            growth = sum(percentages) / len(percentages) if percentages else None
            portfolio_items = getattr(
                getattr(student, "portfolio", None),
                "prefetched_portfolio_items",
                [],
            )
            latest_portfolio = portfolio_items[0] if portfolio_items else None

            profile_photo = None
            if student.user.profile_photo:
                try:
                    profile_photo = request.build_absolute_uri(student.user.profile_photo.url)
                except ValueError:
                    profile_photo = None

            results.append({
                "id": str(student.id),
                "full_name": student.user.full_name,
                "first_name": student.user.first_name,
                "initials": student.user.initials,
                "profile_photo": profile_photo,
                "admission_number": student.admission_number,
                "date_of_birth": student.date_of_birth,
                "age": student_age(student.date_of_birth),
                "school": str(student.school_id),
                "school_name": student.school.name,
                "relationship": relationship.relationship,
                "can_view_reports": relationship.can_view_reports,
                "is_primary_contact": relationship.is_primary_contact,
                "classroom": {
                    "id": str(enrollment.classroom_id),
                    "name": enrollment.classroom.name,
                    "academic_year": enrollment.academic_year.name,
                    "term": enrollment.term.term_number,
                    "status": enrollment.status,
                } if enrollment else None,
                "attendance_rate": attendance_rate,
                "growth_index": round(growth, 1) if growth is not None else None,
                "latest_portfolio": {
                    "id": str(latest_portfolio.id),
                    "title": latest_portfolio.title,
                    "description": latest_portfolio.description,
                    "event_date": latest_portfolio.event_date,
                    "item_type": latest_portfolio.item_type,
                } if latest_portfolio else None,
            })

        return Response({"results": results})

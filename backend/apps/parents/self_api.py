from django.db.models import Avg
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.assessments.models import AssessmentEvaluation
from apps.assessments.permissions import UserRole, get_user_role
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.portfolio.models import PortfolioItem

from .models import ParentStudentRelationship


class ParentChildrenView(views.APIView):
    """Return only the learners linked to the authenticated parent."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if get_user_role(request.user) != UserRole.PARENT:
            raise PermissionDenied("Only parent accounts can access linked learners.")

        relationships = ParentStudentRelationship.objects.filter(
            parent__user=request.user,
            parent__is_active=True,
            is_active=True,
            student__is_active=True,
        ).select_related("student__user", "student__school")

        results = []
        for relationship in relationships:
            student = relationship.student
            enrollment = Enrollment.objects.filter(student=student).select_related(
                "classroom", "academic_year", "term"
            ).order_by("-academic_year__start_date", "-term__term_number").first()

            attendance = AttendanceRecord.objects.filter(enrollment__student=student)
            attendance_total = attendance.count()
            attendance_present = attendance.filter(status__in=["PRESENT", "LATE"]).count()
            attendance_rate = round(attendance_present * 100 / attendance_total, 1) if attendance_total else None

            growth = AssessmentEvaluation.objects.filter(
                submission__enrollment__student=student,
                published=True,
                percentage__isnull=False,
            ).aggregate(value=Avg("percentage"))["value"]

            latest_portfolio = PortfolioItem.objects.filter(
                portfolio__student=student
            ).order_by("-event_date", "-created_at").first()

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
                "age": student.age,
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
                "growth_index": round(float(growth), 1) if growth is not None else None,
                "latest_portfolio": {
                    "id": str(latest_portfolio.id),
                    "title": latest_portfolio.title,
                    "description": latest_portfolio.description,
                    "event_date": latest_portfolio.event_date,
                    "item_type": latest_portfolio.item_type,
                } if latest_portfolio else None,
            })

        return Response({"results": results})

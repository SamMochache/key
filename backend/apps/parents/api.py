from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.schools.models import School
from apps.students.models import Student

from .models import Parent, ParentStudentRelationship

User = get_user_model()


class ParentManagementView(views.APIView):
    """Staff-only parent account and student-link management."""

    permission_classes = [permissions.IsAuthenticated]

    def _staff(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can manage parent accounts.")
        return role, get_user_school(request.user)

    def get(self, request):
        role, school = self._staff(request)
        parents = Parent.objects.select_related("user", "school").prefetch_related("student_relationships__student__user")
        if role != UserRole.ADMIN and school is not None:
            parents = parents.filter(school_id=school.id)
        search = request.query_params.get("search", "").strip()
        if search:
            parents = parents.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
            )
        results = []
        for parent in parents[:100]:
            links = parent.student_relationships.filter(is_active=True).select_related("student__user")
            results.append({
                "id": str(parent.id),
                "user": str(parent.user_id),
                "full_name": parent.user.full_name,
                "email": parent.user.email,
                "phone_number": parent.user.phone_number,
                "school": str(parent.school_id),
                "school_name": parent.school.name,
                "is_active": parent.is_active and parent.user.is_active,
                "students": [
                    {
                        "id": str(link.student_id),
                        "name": link.student.user.full_name,
                        "admission_number": link.student.admission_number,
                        "relationship": link.relationship,
                        "can_view_reports": link.can_view_reports,
                        "is_primary_contact": link.is_primary_contact,
                    }
                    for link in links
                ],
            })
        return Response({"results": results})

    @transaction.atomic
    def post(self, request):
        role, staff_school = self._staff(request)
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password")
        first_name = str(request.data.get("first_name", "")).strip()
        last_name = str(request.data.get("last_name", "")).strip()
        phone_number = str(request.data.get("phone_number", "")).strip()
        school_id = request.data.get("school")
        student_id = request.data.get("student")
        relationship = request.data.get("relationship", ParentStudentRelationship.Relationship.PARENT)
        primary = bool(request.data.get("is_primary_contact", False))
        can_view_reports = bool(request.data.get("can_view_reports", True))

        if not all([email, password, first_name, last_name, school_id, student_id]):
            return Response({"detail": "First name, last name, email, password, school, and student are required."}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"detail": "A user with this email already exists."}, status=409)

        school = School.objects.filter(id=school_id, is_active=True).first()
        if school is None:
            return Response({"detail": "The selected school was not found."}, status=404)
        if role != UserRole.ADMIN and (staff_school is None or school.id != staff_school.id):
            raise PermissionDenied("You can only create parent accounts for your institution.")

        student = Student.objects.filter(id=student_id, school_id=school.id, is_active=True).select_related("user").first()
        if student is None:
            return Response({"detail": "The selected student does not belong to the selected institution."}, status=404)
        if relationship not in dict(ParentStudentRelationship.Relationship.choices):
            return Response({"detail": "Invalid relationship type."}, status=400)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        parent = Parent.objects.create(user=user, school=school)
        if ParentStudentRelationship.objects.filter(parent=parent, student=student).exists():
            return Response({"detail": "This parent is already linked to the selected student."}, status=400)
        link = ParentStudentRelationship.objects.create(
            parent=parent,
            student=student,
            relationship=relationship,
            can_view_reports=can_view_reports,
            is_primary_contact=primary,
        )
        return Response({
            "id": str(parent.id),
            "full_name": parent.user.full_name,
            "email": parent.user.email,
            "school": str(parent.school_id),
            "student": {
                "id": str(link.student_id),
                "name": link.student.user.full_name,
                "admission_number": link.student.admission_number,
            },
        }, status=status.HTTP_201_CREATED)

    def patch(self, request):
        role, staff_school = self._staff(request)
        parent_id = request.data.get("id")
        if not parent_id:
            return Response({"detail": "Parent id is required."}, status=400)
        parent = Parent.objects.select_related("user", "school").filter(id=parent_id).first()
        if parent is None:
            return Response({"detail": "Parent not found."}, status=404)
        if role != UserRole.ADMIN and (staff_school is None or parent.school_id != staff_school.id):
            raise PermissionDenied("The parent does not belong to your institution.")

        for field in ("first_name", "last_name", "phone_number"):
            if field in request.data:
                setattr(parent.user, field, str(request.data[field]).strip())
        if "is_active" in request.data:
            parent.is_active = bool(request.data["is_active"])
            parent.user.is_active = parent.is_active
        parent.user.save(update_fields=["first_name", "last_name", "phone_number", "is_active", "updated_at"])
        parent.save(update_fields=["is_active", "updated_at"])
        return Response({"id": str(parent.id), "full_name": parent.user.full_name, "is_active": parent.is_active})

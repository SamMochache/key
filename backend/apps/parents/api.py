from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.assessments.permissions import UserRole, get_user_role, get_user_school, teacher_can_access_enrollment
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

    def _teacher_parent_scope(self, request):
        return Parent.objects.filter(
            student_relationships__student__enrollments__classroom__teacher_assignments__teacher=request.user.teacher_profile,
            student_relationships__student__enrollments__classroom__teacher_assignments__is_active=True,
            student_relationships__is_active=True,
        ).distinct()

    def get(self, request):
        role, school = self._staff(request)
        if role == UserRole.TEACHER:
            parents = self._teacher_parent_scope(request)
        else:
            parents = Parent.objects.all()
            if school is not None:
                parents = parents.filter(school_id=school.id)
        parents = parents.select_related("user", "school").prefetch_related("student_relationships__student__user")
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
            if role == UserRole.TEACHER:
                links = links.filter(
                    student__enrollments__classroom__teacher_assignments__teacher=request.user.teacher_profile,
                    student__enrollments__classroom__teacher_assignments__is_active=True,
                ).distinct()
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

        if not all([email, first_name, last_name, school_id, student_id]):
            return Response({"detail": "First name, last name, email, school, and student are required."}, status=400)
        if relationship not in dict(ParentStudentRelationship.Relationship.choices):
            return Response({"detail": "Invalid relationship type."}, status=400)

        school = School.objects.filter(id=school_id, is_active=True).first()
        if school is None:
            return Response({"detail": "The selected school was not found."}, status=404)
        if role != UserRole.ADMIN and (staff_school is None or school.id != staff_school.id):
            raise PermissionDenied("You can only manage parent accounts for your institution.")

        student = Student.objects.filter(id=student_id, school_id=school.id, is_active=True).select_related("user").first()
        if student is None:
            return Response({"detail": "The selected student does not belong to the selected institution."}, status=404)
        if role == UserRole.TEACHER:
            if not student.enrollments.filter(
                classroom__teacher_assignments__teacher=request.user.teacher_profile,
                classroom__teacher_assignments__is_active=True,
            ).exists():
                raise PermissionDenied("You can only manage parents for learners in your assigned classrooms.")

        existing_user = User.objects.filter(email=email).first()
        if existing_user is not None:
            parent = getattr(existing_user, "parent_profile", None)
            if parent is None:
                return Response({"detail": "A user with this email already exists and is not a parent account."}, status=409)
            if parent.school_id != school.id:
                raise PermissionDenied("The existing parent belongs to another institution.")
            if ParentStudentRelationship.objects.filter(parent=parent, student=student).exists():
                return Response({"detail": "This parent is already linked to the selected student."}, status=409)
        else:
            if not password:
                return Response({"detail": "A password is required when creating a new parent account."}, status=400)
            existing_user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )
            parent = Parent.objects.create(user=existing_user, school=school)

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
        if role == UserRole.TEACHER and not self._teacher_parent_scope(request).filter(id=parent.id).exists():
            raise PermissionDenied("You can only manage parents linked to learners in your assigned classrooms.")

        for field in ("first_name", "last_name", "phone_number"):
            if field in request.data:
                setattr(parent.user, field, str(request.data[field]).strip())
        if "is_active" in request.data:
            parent.is_active = bool(request.data["is_active"])
            parent.user.is_active = parent.is_active
        parent.user.save(update_fields=["first_name", "last_name", "phone_number", "is_active", "updated_at"])
        parent.save(update_fields=["is_active", "updated_at"])
        return Response({"id": str(parent.id), "full_name": parent.user.full_name, "is_active": parent.is_active})

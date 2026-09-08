from rest_framework import permissions, viewsets

from apps.assessments.permissions import UserRole, get_user_role, get_user_school

from .models import Student
from .serializers import StudentSerializer


class StudentAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access this student."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = get_user_role(user)
        if request.method in permissions.SAFE_METHODS:
            return role in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT}
        return role in {UserRole.ADMIN, UserRole.TEACHER}

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = get_user_role(user)
        school = get_user_school(user)

        if role == UserRole.ADMIN:
            return school is None or obj.school_id == school.id

        if role == UserRole.STUDENT:
            return request.method in permissions.SAFE_METHODS and obj.pk == user.student_profile.pk

        if role == UserRole.TEACHER:
            if obj.school_id != user.teacher_profile.school_id:
                return False
            if request.method not in permissions.SAFE_METHODS:
                return obj.enrollments.filter(
                    classroom__teacher_subjects__teacher=user.teacher_profile,
                    classroom__teacher_subjects__is_active=True,
                ).exists()
            return True

        return False


class StudentViewSet(viewsets.ModelViewSet):
    """Student directory with institution and teacher-assignment isolation."""

    serializer_class = StudentSerializer
    permission_classes = [StudentAccessPermission]

    def get_queryset(self):
        queryset = Student.objects.select_related("user", "school").all()
        user = self.request.user
        role = get_user_role(user)
        school = get_user_school(user)

        if role == UserRole.ADMIN:
            if school is not None:
                queryset = queryset.filter(school_id=school.id)
        elif role == UserRole.TEACHER:
            queryset = queryset.filter(
                school_id=user.teacher_profile.school_id,
                enrollments__classroom__teacher_subjects__teacher=user.teacher_profile,
                enrollments__classroom__teacher_subjects__is_active=True,
            ).distinct()
        elif role == UserRole.STUDENT:
            queryset = queryset.filter(pk=user.student_profile.pk)
        else:
            return queryset.none()

        search = self.request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(admission_number__icontains=search)
            )

        gender = self.request.query_params.get("gender", "").strip()
        if gender:
            queryset = queryset.filter(gender=gender)

        active = self.request.query_params.get("is_active")
        if active in {"true", "false"}:
            queryset = queryset.filter(is_active=active == "true")

        return queryset

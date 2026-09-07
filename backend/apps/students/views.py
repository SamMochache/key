from rest_framework import permissions, viewsets

from .models import Student
from .serializers import StudentSerializer


class StudentAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access this student."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return self._is_admin(user) or self._user_school(user) is not None

        return self._is_admin(user) or getattr(user, "teacher_profile", None) is not None

    def has_object_permission(self, request, view, obj):
        user = request.user
        if self._is_admin(user):
            return True

        student_profile = getattr(user, "student_profile", None)
        if student_profile is not None:
            return request.method in permissions.SAFE_METHODS and obj.pk == student_profile.pk

        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile is not None:
            return obj.school_id == teacher_profile.school_id

        return False

    @staticmethod
    def _is_admin(user):
        return bool(user.is_staff or user.is_superuser)

    @staticmethod
    def _user_school(user):
        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile is not None:
            return teacher_profile.school
        student_profile = getattr(user, "student_profile", None)
        if student_profile is not None:
            return student_profile.school
        return None


class StudentViewSet(viewsets.ModelViewSet):
    """Student directory with strict institution-level tenant isolation."""

    serializer_class = StudentSerializer
    permission_classes = [StudentAccessPermission]

    def get_queryset(self):
        queryset = Student.objects.select_related("user", "school").all()
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return queryset

        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile is not None:
            queryset = queryset.filter(school_id=teacher_profile.school_id)
        else:
            student_profile = getattr(user, "student_profile", None)
            if student_profile is not None:
                queryset = queryset.filter(pk=student_profile.pk)
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

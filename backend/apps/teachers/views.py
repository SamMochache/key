from rest_framework import permissions, viewsets

from .models.department import Department
from .models.teacher import Teacher
from .serializers import DepartmentSerializer, TeacherSerializer


class InstitutionAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


class TeacherAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access this teacher."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return self._is_admin(user) or self._user_school(user) is not None
        return self._is_admin(user)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if self._is_admin(user):
            return True
        return request.method in permissions.SAFE_METHODS and obj.school_id == self._user_school_id(user)

    @staticmethod
    def _is_admin(user):
        return bool(user.is_staff or user.is_superuser)

    @staticmethod
    def _user_school(user):
        profile = getattr(user, "teacher_profile", None) or getattr(user, "student_profile", None)
        return getattr(profile, "school", None)

    @classmethod
    def _user_school_id(cls, user):
        school = cls._user_school(user)
        return school.pk if school else None


class TeacherViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherSerializer
    permission_classes = [TeacherAccessPermission]

    def get_queryset(self):
        queryset = Teacher.objects.select_related("user", "school", "department").all()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            school_id = TeacherAccessPermission._user_school_id(user)
            queryset = queryset.filter(school_id=school_id) if school_id else queryset.none()
        search = self.request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q
            queryset = queryset.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(user__email__icontains=search) | Q(employee_number__icontains=search) | Q(department__name__icontains=search))
        teacher_status = self.request.query_params.get("status", "").strip()
        if teacher_status:
            queryset = queryset.filter(status=teacher_status)
        employment_type = self.request.query_params.get("employment_type", "").strip()
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        return queryset


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [InstitutionAdminPermission]

    def get_queryset(self):
        queryset = Department.objects.select_related("school").all()
        school = self.request.query_params.get("school")
        if school:
            queryset = queryset.filter(school_id=school)
        return queryset

from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.assessments.permissions import UserRole, get_user_role, get_user_school

from .models.department import Department
from .models.teacher import Teacher
from .models.teacher_subject import TeacherSubject
from .serializers import DepartmentSerializer, TeacherSerializer, TeacherSubjectSerializer


class InstitutionAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and get_user_role(request.user) == UserRole.ADMIN)


class TeacherAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access this teacher."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = get_user_role(user)
        if request.method in permissions.SAFE_METHODS:
            return role in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT}
        return role == UserRole.ADMIN

    def has_object_permission(self, request, view, obj):
        role = get_user_role(request.user)
        school = get_user_school(request.user)
        if role == UserRole.ADMIN:
            return school is None or obj.school_id == school.id
        return request.method in permissions.SAFE_METHODS and school is not None and obj.school_id == school.id


class TeacherViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherSerializer
    permission_classes = [TeacherAccessPermission]

    def get_queryset(self):
        queryset = Teacher.objects.select_related("user", "school", "department").all()
        role = get_user_role(self.request.user)
        school = get_user_school(self.request.user)
        if role != UserRole.ADMIN or school is not None:
            queryset = queryset.filter(school_id=school.id) if school else queryset.none()
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

    def perform_create(self, serializer):
        school = get_user_school(self.request.user)
        if school is not None:
            serializer.save(school=school)
        else:
            serializer.save()

    def perform_update(self, serializer):
        school = get_user_school(self.request.user)
        if school is not None and serializer.instance.school_id != school.id:
            raise PermissionDenied("The teacher does not belong to your institution.")
        serializer.save()


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [InstitutionAdminPermission]

    def get_queryset(self):
        queryset = Department.objects.select_related("school").all()
        own_school = get_user_school(self.request.user)
        if own_school is not None:
            return queryset.filter(school_id=own_school.id)
        school = self.request.query_params.get("school")
        if school:
            queryset = queryset.filter(school_id=school)
        return queryset

    def perform_create(self, serializer):
        school = get_user_school(self.request.user)
        if school is not None:
            serializer.save(school=school)
        else:
            serializer.save()


class TeacherSubjectAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access teacher subject assignments."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and get_user_role(request.user) in {
            UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT
        })


class TeacherSubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeacherSubjectSerializer
    permission_classes = [TeacherSubjectAccessPermission]

    def get_queryset(self):
        queryset = TeacherSubject.objects.select_related(
            "teacher__user", "teacher__school", "subject", "classroom", "academic_year", "term"
        )
        user = self.request.user
        role = get_user_role(user)
        school = get_user_school(user)

        if role == UserRole.ADMIN:
            if school is not None:
                queryset = queryset.filter(classroom__school_id=school.id)
        elif role == UserRole.TEACHER:
            queryset = queryset.filter(teacher=user.teacher_profile)
        elif role == UserRole.STUDENT:
            queryset = queryset.filter(
                classroom__enrollments__student=user.student_profile,
                classroom__enrollments__academic_year=models.F("academic_year"),
                classroom__enrollments__term=models.F("term"),
            ).distinct()
        else:
            return queryset.none()

        for param, field in (
            ("school", "teacher__school_id"),
            ("classroom", "classroom_id"),
            ("academic_year", "academic_year_id"),
            ("term", "term_id"),
            ("teacher", "teacher_id"),
            ("subject", "subject_id"),
        ):
            value = self.request.query_params.get(param)
            if value:
                queryset = queryset.filter(**{field: value})
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        return queryset

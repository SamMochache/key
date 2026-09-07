from django.db.models import Q
from rest_framework import permissions, viewsets

from .models import Enrollment
from .serializers import EnrollmentSerializer


def user_school_id(user):
    teacher = getattr(user, "teacher_profile", None)
    if teacher is not None:
        return teacher.school_id
    student = getattr(user, "student_profile", None)
    if student is not None:
        return student.school_id
    return None


def is_admin(user):
    return bool(user.is_staff or user.is_superuser)


class EnrollmentAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access enrollment data."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return is_admin(user) or user_school_id(user) is not None
        return is_admin(user) or getattr(user, "teacher_profile", None) is not None

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        school_id = user_school_id(request.user)
        if request.method in permissions.SAFE_METHODS:
            return obj.classroom.school_id == school_id
        teacher = getattr(request.user, "teacher_profile", None)
        return teacher is not None and obj.classroom.school_id == teacher.school_id


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [EnrollmentAccessPermission]

    def get_queryset(self):
        queryset = Enrollment.objects.select_related(
            "student__user",
            "classroom",
            "academic_year",
            "term",
        ).all()

        if not is_admin(self.request.user):
            school_id = user_school_id(self.request.user)
            if not school_id:
                return queryset.none()
            queryset = queryset.filter(classroom__school_id=school_id)

            student_profile = getattr(self.request.user, "student_profile", None)
            if student_profile is not None:
                queryset = queryset.filter(student_id=student_profile.id)

        student = self.request.query_params.get("student")
        classroom = self.request.query_params.get("classroom")
        academic_year = self.request.query_params.get("academic_year")
        term = self.request.query_params.get("term")
        status = self.request.query_params.get("status")
        search = self.request.query_params.get("search", "").strip()

        if student:
            queryset = queryset.filter(student_id=student)
        if classroom:
            queryset = queryset.filter(classroom_id=classroom)
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        if term:
            queryset = queryset.filter(term_id=term)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search)
                | Q(student__user__last_name__icontains=search)
                | Q(student__user__email__icontains=search)
                | Q(student__admission_number__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save()

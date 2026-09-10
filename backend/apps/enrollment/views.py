from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.assessments.permissions import UserRole, get_user_role, get_user_school, teacher_can_access_classroom
from core.constants.enrollment import EnrollmentStatus

from .models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollmentAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access enrollment data."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request.user)
        if request.method in permissions.SAFE_METHODS:
            return role in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT}
        return role == UserRole.ADMIN

    def has_object_permission(self, request, view, obj):
        role = get_user_role(request.user)
        school = get_user_school(request.user)
        if role == UserRole.ADMIN:
            return school is None or obj.classroom.school_id == school.id
        if role == UserRole.STUDENT:
            return request.method in permissions.SAFE_METHODS and obj.student_id == request.user.student_profile.id
        if role == UserRole.TEACHER:
            return request.method in permissions.SAFE_METHODS and teacher_can_access_classroom(request.user, obj.classroom_id)
        return False


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
        user = self.request.user
        role = get_user_role(user)
        school = get_user_school(user)

        if role == UserRole.ADMIN:
            if school is not None:
                queryset = queryset.filter(classroom__school_id=school.id)
        elif role == UserRole.TEACHER:
            teacher = getattr(user, "teacher_profile", None)
            if teacher is None:
                return queryset.none()
            queryset = queryset.filter(
                classroom__teacher_assignments__teacher_id=teacher.id,
                classroom__teacher_assignments__is_active=True,
            ).distinct()
        elif role == UserRole.STUDENT:
            queryset = queryset.filter(student_id=user.student_profile.id)
        else:
            return queryset.none()

        student = self.request.query_params.get("student")
        classroom = self.request.query_params.get("classroom")
        academic_year = self.request.query_params.get("academic_year")
        term = self.request.query_params.get("term")
        requested_status = self.request.query_params.get("status")
        search = self.request.query_params.get("search", "").strip()

        if student:
            queryset = queryset.filter(student_id=student)
        if classroom:
            if role == UserRole.TEACHER and not teacher_can_access_classroom(user, classroom):
                return queryset.none()
            queryset = queryset.filter(classroom_id=classroom)
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        if term:
            queryset = queryset.filter(term_id=term)
        if requested_status:
            # Older frontend code used ACTIVE before the enrollment lifecycle was
            # finalized. Preserve that request as a compatibility alias while the
            # canonical database value remains ENROLLED.
            if requested_status == "ACTIVE":
                requested_status = EnrollmentStatus.ENROLLED
            queryset = queryset.filter(status=requested_status)
        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search)
                | Q(student__user__last_name__icontains=search)
                | Q(student__user__email__icontains=search)
                | Q(student__admission_number__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        school = get_user_school(self.request.user)
        classroom = serializer.validated_data.get("classroom")
        student = serializer.validated_data.get("student")
        if school is not None:
            if classroom is None or classroom.school_id != school.id:
                raise PermissionDenied("The classroom does not belong to your institution.")
            if student is None or student.school_id != school.id:
                raise PermissionDenied("The student does not belong to your institution.")
        serializer.save()

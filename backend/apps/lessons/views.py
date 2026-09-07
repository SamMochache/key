from django.db.models import Q
from rest_framework import permissions, viewsets

from .models import LessonSession
from .serializers import LessonSessionSerializer


def school_id_for(user):
    teacher = getattr(user, "teacher_profile", None)
    if teacher is not None:
        return teacher.school_id
    student = getattr(user, "student_profile", None)
    if student is not None:
        return student.school_id
    return None


def is_admin(user):
    return bool(user.is_staff or user.is_superuser)


class LessonAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return is_admin(request.user) or school_id_for(request.user) is not None
        return is_admin(request.user) or getattr(request.user, "teacher_profile", None) is not None

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        school_id = school_id_for(request.user)
        return obj.classroom.school_id == school_id


class LessonSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSessionSerializer
    permission_classes = [LessonAccessPermission]

    def get_queryset(self):
        qs = LessonSession.objects.select_related(
            "classroom", "subject", "teacher", "term", "classroom__school",
        )
        if not is_admin(self.request.user):
            qs = qs.filter(classroom__school_id=school_id_for(self.request.user))
            student = getattr(self.request.user, "student_profile", None)
            if student is not None:
                qs = qs.filter(classroom__enrollments__student_id=student.id)
        for param, field in (("classroom", "classroom_id"), ("subject", "subject_id"), ("teacher", "teacher_id"), ("term", "term_id"), ("status", "status"), ("lesson_date", "lesson_date")):
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return qs

    def perform_create(self, serializer):
        teacher = serializer.validated_data["teacher"]
        if not is_admin(self.request.user):
            profile = getattr(self.request.user, "teacher_profile", None)
            if profile is None or teacher.id != self.request.user.id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Teachers can only create lessons assigned to themselves.")
        serializer.save()

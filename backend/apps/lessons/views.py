from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

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
    message = "You do not have permission to access lesson data."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return is_admin(request.user) or school_id_for(request.user) is not None
        return is_admin(request.user) or getattr(request.user, "teacher_profile", None) is not None

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        return obj.timetable_entry.classroom.school_id == school_id_for(request.user)


class LessonSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSessionSerializer
    permission_classes = [LessonAccessPermission]

    def get_queryset(self):
        qs = LessonSession.objects.select_related(
            "teacher", "timetable_entry__classroom", "timetable_entry__period",
            "timetable_entry__teacher_subject__teacher__user",
            "timetable_entry__teacher_subject__subject",
            "timetable_entry__timetable__term",
        )
        if not is_admin(self.request.user):
            qs = qs.filter(timetable_entry__classroom__school_id=school_id_for(self.request.user))
            student = getattr(self.request.user, "student_profile", None)
            if student is not None:
                qs = qs.filter(timetable_entry__classroom__enrollments__student_id=student.id)
        filters = {
            "classroom": "timetable_entry__classroom_id",
            "teacher": "teacher_id",
            "term": "timetable_entry__timetable__term_id",
            "status": "status",
            "lesson_date": "lesson_date",
        }
        for param, field in filters.items():
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        subject = self.request.query_params.get("subject")
        if subject:
            qs = qs.filter(timetable_entry__teacher_subject__subject_id=subject)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(Q(remarks__icontains=search) | Q(timetable_entry__classroom__name__icontains=search))
        return qs.distinct()

    def perform_create(self, serializer):
        teacher = serializer.validated_data["teacher"]
        if not is_admin(self.request.user) and teacher.id != self.request.user.id:
            raise PermissionDenied("Teachers can only create lessons assigned to themselves.")
        serializer.save()

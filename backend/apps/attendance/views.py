from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models.attendance_register import AttendanceRegister
from .serializers import AttendanceBulkSerializer, AttendanceRegisterSerializer


def is_admin(user):
    return bool(user.is_staff or user.is_superuser)


class AttendanceAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access attendance."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            is_admin(request.user) or getattr(request.user, "teacher_profile", None) is not None
        ))


class AttendanceRegisterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceRegisterSerializer
    permission_classes = [AttendanceAccessPermission]

    def get_queryset(self):
        queryset = AttendanceRegister.objects.select_related(
            "lesson_session__teacher",
            "lesson_session__timetable_entry__classroom",
            "lesson_session__timetable_entry__teacher_subject__subject",
        ).prefetch_related("records__enrollment__student__user")

        if not is_admin(self.request.user):
            queryset = queryset.filter(lesson_session__teacher=self.request.user)

        lesson_session = self.request.query_params.get("lesson_session")
        lesson_date = self.request.query_params.get("lesson_date")
        classroom = self.request.query_params.get("classroom")
        if lesson_session:
            queryset = queryset.filter(lesson_session_id=lesson_session)
        if lesson_date:
            queryset = queryset.filter(lesson_session__lesson_date=lesson_date)
        if classroom:
            queryset = queryset.filter(lesson_session__timetable_entry__classroom_id=classroom)
        return queryset.order_by("-lesson_session__lesson_date")

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk(self, request):
        serializer = AttendanceBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.validated_data["lesson"]
        if not is_admin(request.user) and lesson.teacher_id != request.user.id:
            return Response({"detail": "You can only record attendance for your own lessons."}, status=status.HTTP_403_FORBIDDEN)
        register = serializer.save()
        return Response(AttendanceRegisterSerializer(register).data)

    @action(detail=True, methods=["post"], url_path="lock")
    def lock(self, request, pk=None):
        register = self.get_object()
        if not is_admin(request.user) and register.lesson_session.teacher_id != request.user.id:
            return Response({"detail": "You can only lock your own attendance registers."}, status=status.HTTP_403_FORBIDDEN)
        if register.status != "SUBMITTED":
            return Response({"detail": "Only submitted registers can be locked."}, status=status.HTTP_400_BAD_REQUEST)
        from django.utils import timezone
        register.status = "LOCKED"
        register.locked_at = timezone.now()
        register.save(update_fields=["status", "locked_at", "updated_at"])
        return Response(AttendanceRegisterSerializer(register).data)

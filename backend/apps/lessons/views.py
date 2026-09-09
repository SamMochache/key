from datetime import date

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.timetables.models.timetable_entry import TimetableEntry
from core.constants.timetable import TimetableStatus, WeekDay

from .models import LessonSession
from .serializers import LessonSessionSerializer


def school_id_for(user):
    school_admin = getattr(user, "school_admin_profile", None)
    if school_admin is not None and school_admin.is_active:
        return school_admin.school_id
    teacher = getattr(user, "teacher_profile", None)
    if teacher is not None:
        return teacher.school_id
    student = getattr(user, "student_profile", None)
    if student is not None:
        return student.school_id
    return None


def is_platform_admin(user):
    school_admin = getattr(user, "school_admin_profile", None)
    return bool(user.is_superuser or (user.is_staff and not school_admin))


def is_admin(user):
    school_admin = getattr(user, "school_admin_profile", None)
    return bool(
        is_platform_admin(user)
        or (school_admin is not None and school_admin.is_active)
    )


def weekday_for(day):
    values = {
        0: WeekDay.MONDAY,
        1: WeekDay.TUESDAY,
        2: WeekDay.WEDNESDAY,
        3: WeekDay.THURSDAY,
        4: WeekDay.FRIDAY,
    }
    return values.get(day.weekday())


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
        teacher = getattr(request.user, "teacher_profile", None)
        if teacher is not None:
            return obj.teacher_id == request.user.id
        return obj.timetable_entry.classroom.school_id == school_id_for(request.user)


class LessonSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSessionSerializer
    permission_classes = [LessonAccessPermission]

    def get_queryset(self):
        qs = LessonSession.objects.select_related(
            "teacher",
            "timetable_entry__classroom",
            "timetable_entry__period",
            "timetable_entry__teacher_subject__teacher__user",
            "timetable_entry__teacher_subject__subject",
            "timetable_entry__timetable__term",
        )
        if not is_platform_admin(self.request.user):
            school_id = school_id_for(self.request.user)
            qs = qs.filter(timetable_entry__classroom__school_id=school_id)
            teacher = getattr(self.request.user, "teacher_profile", None)
            student = getattr(self.request.user, "student_profile", None)
            school_admin = getattr(self.request.user, "school_admin_profile", None)
            if teacher is not None and not (school_admin is not None and school_admin.is_active):
                qs = qs.filter(teacher_id=self.request.user.id)
            elif student is not None and not (school_admin is not None and school_admin.is_active):
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
            qs = qs.filter(
                Q(remarks__icontains=search)
                | Q(timetable_entry__classroom__name__icontains=search)
                | Q(timetable_entry__teacher_subject__subject__name__icontains=search)
            )
        return qs.distinct()

    def perform_create(self, serializer):
        teacher = serializer.validated_data["teacher"]
        if not is_admin(self.request.user) and teacher.id != self.request.user.id:
            raise PermissionDenied("Teachers can only create lessons assigned to themselves.")
        serializer.save()

    def _require_assigned_teacher(self, lesson):
        if is_admin(self.request.user):
            return
        if lesson.teacher_id != self.request.user.id:
            raise PermissionDenied("You can only manage lessons assigned to you.")

    @action(detail=False, methods=["post"], url_path="sync-day")
    def sync_day(self, request):
        teacher = getattr(request.user, "teacher_profile", None)
        if teacher is None:
            raise PermissionDenied("Only teacher accounts can sync timetable lessons.")

        raw_date = request.data.get("lesson_date")
        if raw_date:
            try:
                lesson_date = date.fromisoformat(raw_date)
            except (TypeError, ValueError):
                raise ValidationError({"lesson_date": "Use YYYY-MM-DD format."})
        else:
            lesson_date = timezone.localdate()

        weekday = weekday_for(lesson_date)
        if weekday is None:
            return Response({"created": 0, "lesson_date": lesson_date, "lessons": []})

        entries = TimetableEntry.objects.select_related(
            "timetable__term",
            "teacher_subject__teacher__user",
        ).filter(
            timetable__school_id=teacher.school_id,
            timetable__status=TimetableStatus.PUBLISHED,
            timetable__effective_from__lte=lesson_date,
            timetable__term__start_date__lte=lesson_date,
            timetable__term__end_date__gte=lesson_date,
            weekday=weekday,
            classroom__is_active=True,
            teacher_subject__teacher=teacher,
            teacher_subject__is_active=True,
        ).filter(Q(timetable__effective_to__isnull=True) | Q(timetable__effective_to__gte=lesson_date))

        created_count = 0
        lesson_ids = []
        with transaction.atomic():
            for entry in entries:
                lesson, created = LessonSession.objects.get_or_create(
                    timetable_entry=entry,
                    lesson_date=lesson_date,
                    defaults={
                        "teacher": request.user,
                        "status": LessonSession.Status.SCHEDULED,
                    },
                )
                lesson_ids.append(lesson.id)
                if created:
                    created_count += 1

        lessons = self.get_queryset().filter(id__in=lesson_ids).order_by("timetable_entry__period__sequence")
        return Response(
            {
                "created": created_count,
                "lesson_date": lesson_date,
                "lessons": self.get_serializer(lessons, many=True).data,
            }
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        lesson = self.get_object()
        self._require_assigned_teacher(lesson)
        if lesson.status != LessonSession.Status.SCHEDULED:
            raise ValidationError({"status": "Only scheduled lessons can be started."})

        lesson.status = LessonSession.Status.IN_PROGRESS
        lesson.started_at = timezone.now()
        lesson.ended_at = None
        lesson.save(update_fields=["status", "started_at", "ended_at", "updated_at"])
        return Response(self.get_serializer(lesson).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        lesson = self.get_object()
        self._require_assigned_teacher(lesson)
        if lesson.status != LessonSession.Status.IN_PROGRESS:
            raise ValidationError({"status": "Only lessons in progress can be completed."})

        lesson.status = LessonSession.Status.COMPLETED
        lesson.ended_at = timezone.now()
        if "remarks" in request.data:
            lesson.remarks = str(request.data.get("remarks") or "").strip()
        lesson.save(update_fields=["status", "ended_at", "remarks", "updated_at"])
        return Response(self.get_serializer(lesson).data, status=status.HTTP_200_OK)

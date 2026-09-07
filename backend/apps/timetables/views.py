from django.db import transaction
from django.db.models import Count
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.constants.timetable import TimetableStatus

from .models.period import Period
from .models.timetable import Timetable
from .models.timetable_entry import TimetableEntry
from .serializers import PeriodSerializer, TimetableEntrySerializer, TimetableSerializer


def is_admin(user):
    return bool(user.is_staff or user.is_superuser)


def user_school(user):
    teacher = getattr(user, "teacher_profile", None)
    if teacher is not None:
        return teacher.school
    student = getattr(user, "student_profile", None)
    if student is not None:
        return student.school
    return None


class TimetableAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access timetable data."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return is_admin(request.user) or user_school(request.user) is not None
        return is_admin(request.user)


class PeriodViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodSerializer
    permission_classes = [TimetableAccessPermission]

    def get_queryset(self):
        queryset = Period.objects.select_related("school").all()
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
            queryset = queryset.filter(school=school) if school else queryset.none()
        school_id = self.request.query_params.get("school")
        if is_admin(self.request.user) and school_id:
            queryset = queryset.filter(school_id=school_id)
        return queryset

    def perform_create(self, serializer):
        school = serializer.validated_data.get("school")
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
        if school is None:
            raise ValidationError({"school": "A valid institution is required."})
        serializer.save(school=school)


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    permission_classes = [TimetableAccessPermission]

    def get_queryset(self):
        queryset = Timetable.objects.select_related("school", "academic_year", "term").annotate(
            entry_count=Count("entries", distinct=True)
        )
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
            queryset = queryset.filter(school=school, status=TimetableStatus.PUBLISHED) if school else queryset.none()
        for param, field in (
            ("school", "school_id"),
            ("academic_year", "academic_year_id"),
            ("term", "term_id"),
            ("status", "status"),
        ):
            value = self.request.query_params.get(param)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset

    def perform_create(self, serializer):
        school = serializer.validated_data.get("school")
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
        if school is None:
            raise ValidationError({"school": "A valid institution is required."})
        serializer.save(school=school)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        timetable = self.get_object()
        if timetable.status == TimetableStatus.PUBLISHED:
            return Response(self.get_serializer(timetable).data)
        if timetable.status == TimetableStatus.ARCHIVED:
            raise ValidationError({"status": "Archived timetables cannot be published."})
        if timetable.effective_to and timetable.effective_to < timetable.effective_from:
            raise ValidationError({"effective_to": "Effective end date cannot be before the start date."})
        if not timetable.entries.exists():
            raise ValidationError({"entries": "Add at least one timetable entry before publishing."})
        with transaction.atomic():
            Timetable.objects.filter(
                school=timetable.school,
                academic_year=timetable.academic_year,
                term=timetable.term,
                status=TimetableStatus.PUBLISHED,
            ).exclude(pk=timetable.pk).update(status=TimetableStatus.ARCHIVED)
            timetable.status = TimetableStatus.PUBLISHED
            timetable.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        timetable = self.get_object()
        if timetable.status == TimetableStatus.ARCHIVED:
            return Response(self.get_serializer(timetable).data)
        timetable.status = TimetableStatus.ARCHIVED
        timetable.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(timetable).data)

    @action(detail=True, methods=["post"], url_path="new-version")
    def new_version(self, request, pk=None):
        source = self.get_object()
        next_version = Timetable.objects.filter(
            school=source.school,
            academic_year=source.academic_year,
            term=source.term,
        ).order_by("-version").values_list("version", flat=True).first() or 0
        with transaction.atomic():
            clone = Timetable.objects.create(
                school=source.school,
                academic_year=source.academic_year,
                term=source.term,
                name=source.name,
                version=next_version + 1,
                status=TimetableStatus.DRAFT,
                effective_from=source.effective_from,
                effective_to=source.effective_to,
            )
            for entry in source.entries.all():
                TimetableEntry.objects.create(
                    timetable=clone,
                    weekday=entry.weekday,
                    period=entry.period,
                    classroom=entry.classroom,
                    teacher_subject=entry.teacher_subject,
                    room=entry.room,
                )
        return Response(self.get_serializer(clone).data, status=status.HTTP_201_CREATED)


class TimetableEntryViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableEntrySerializer
    permission_classes = [TimetableAccessPermission]

    def get_queryset(self):
        queryset = TimetableEntry.objects.select_related(
            "timetable", "period", "classroom", "teacher_subject__teacher__user", "teacher_subject__subject"
        )
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
            queryset = queryset.filter(timetable__school=school, timetable__status=TimetableStatus.PUBLISHED) if school else queryset.none()
        for param, field in (
            ("timetable", "timetable_id"),
            ("classroom", "classroom_id"),
            ("period", "period_id"),
            ("teacher_subject", "teacher_subject_id"),
            ("weekday", "weekday"),
        ):
            value = self.request.query_params.get(param)
            if value:
                queryset = queryset.filter(**{field: value})
        if self.request.query_params.get("published") in {"1", "true", "True"}:
            queryset = queryset.filter(timetable__status=TimetableStatus.PUBLISHED)
        return queryset

    def perform_create(self, serializer):
        if not is_admin(self.request.user):
            raise PermissionDenied("Only administrators can create timetable entries.")
        serializer.save()

    def perform_update(self, serializer):
        if not is_admin(self.request.user):
            raise PermissionDenied("Only administrators can update timetable entries.")
        if serializer.instance.timetable.status == TimetableStatus.PUBLISHED:
            raise ValidationError("Published timetables are read-only. Create a new version to make changes.")
        serializer.save()

    def perform_destroy(self, instance):
        if not is_admin(self.request.user):
            raise PermissionDenied("Only administrators can delete timetable entries.")
        if instance.timetable.status == TimetableStatus.PUBLISHED:
            raise ValidationError("Published timetables are read-only. Create a new version to make changes.")
        instance.delete()

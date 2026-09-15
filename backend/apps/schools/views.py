from django.db import transaction
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.platform_admin.models import AuditLog, PlatformSetting

from .models import School
from .permissions import SchoolAccessPermission
from .serializers import SchoolSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    """Institution directory with strict school-level tenant isolation."""

    serializer_class = SchoolSerializer
    permission_classes = [SchoolAccessPermission]

    def get_queryset(self):
        queryset = School.objects.annotate(
            student_count=Count("students", distinct=True),
            teacher_count=Count("teachers", distinct=True),
        )
        user = self.request.user

        admin_profile = getattr(user, "school_admin_profile", None)
        if admin_profile is not None and admin_profile.is_active:
            return queryset.filter(pk=admin_profile.school_id)

        if user.is_staff or user.is_superuser:
            return queryset

        for relation in ("teacher_profile", "student_profile", "parent_profile"):
            profile = getattr(user, relation, None)
            if profile is not None:
                return queryset.filter(pk=profile.school_id)
        return queryset.none()

    @transaction.atomic
    def perform_create(self, serializer):
        school = serializer.save(
            country=serializer.validated_data.get(
                "country",
                _platform_setting("default_country", "Kenya"),
            ),
            timezone=serializer.validated_data.get(
                "timezone",
                _platform_setting("default_timezone", "Africa/Nairobi"),
            ),
        )
        AuditLog.objects.create(
            actor=self.request.user,
            school=school,
            action="INSTITUTION_CREATED",
            resource_type="school",
            resource_id=str(school.id),
            metadata={"name": school.name, "short_name": school.short_name},
        )

    @transaction.atomic
    def perform_update(self, serializer):
        school = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            school=school,
            action="INSTITUTION_UPDATED",
            resource_type="school",
            resource_id=str(school.id),
            metadata={"name": school.name, "short_name": school.short_name},
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        school_id = str(instance.id)
        school_name = instance.name
        super().perform_destroy(instance)
        AuditLog.objects.create(
            actor=self.request.user,
            action="INSTITUTION_DELETED",
            resource_type="school",
            resource_id=school_id,
            metadata={"name": school_name},
        )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Return the authenticated user's own institution."""
        user = request.user
        admin_profile = getattr(user, "school_admin_profile", None)
        if admin_profile is not None and admin_profile.is_active:
            school = self.get_queryset().get(pk=admin_profile.school_id)
            return Response(self.get_serializer(school).data)

        if user.is_staff or user.is_superuser:
            return Response(
                {"detail": "Platform administrators do not have a single institution context."},
                status=status.HTTP_403_FORBIDDEN,
            )

        for relation in ("teacher_profile", "student_profile", "parent_profile"):
            profile = getattr(user, relation, None)
            if profile is not None:
                school = self.get_queryset().get(pk=profile.school_id)
                return Response(self.get_serializer(school).data)

        return Response(
            {"detail": "Your account is not associated with an institution."},
            status=status.HTTP_403_FORBIDDEN,
        )


def _platform_setting(key, fallback):
    setting = PlatformSetting.objects.filter(key=key, is_deleted=False).first()
    if setting is None:
        return fallback
    return setting.value

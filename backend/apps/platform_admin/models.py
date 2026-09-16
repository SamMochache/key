from django.conf import settings
from django.db import models

from core.models import BaseModel
from apps.schools.models import School


class PlatformSetting(BaseModel):
    """Persisted settings owned by the KEY platform, not an individual school."""

    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "platform_settings"
        ordering = ["key"]


class AuditLog(BaseModel):
    """Immutable-style platform audit record for administrative actions."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="platform_audit_events",
    )
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="platform_audit_events",
    )
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "platform_audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["action"]),
            models.Index(fields=["resource_type"]),
        ]

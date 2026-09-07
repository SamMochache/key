from django.conf import settings
from django.db import models

from apps.schools.models import School
from core.models import BaseModel


class Notification(BaseModel):
    class Type(models.TextChoices):
        MESSAGE = "MESSAGE", "Message"
        ASSESSMENT = "ASSESSMENT", "Assessment"
        REPORT = "REPORT", "Report"
        CALENDAR = "CALENDAR", "Calendar"
        TIMETABLE = "TIMETABLE", "Timetable"
        SYSTEM = "SYSTEM", "System"

    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="notifications")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=300, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "read_at", "created_at"]),
            models.Index(fields=["school", "created_at"]),
        ]

    @property
    def is_read(self):
        return self.read_at is not None

    def __str__(self):
        return f"{self.title} → {self.recipient}"

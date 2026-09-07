from django.conf import settings
from django.db import models

from apps.schools.models import BaseModel
from apps.timetables.models import TimetableEntry


class LessonSession(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        MISSED = "MISSED", "Missed"

    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.PROTECT, related_name="lesson_sessions")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="lesson_sessions")
    lesson_date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = "lesson_sessions"
        ordering = ["-lesson_date"]
        constraints = [models.UniqueConstraint(fields=["timetable_entry", "lesson_date"], name="unique_lesson_session")]

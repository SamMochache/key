from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.timetables.models import TimetableEntry
from core.constants.lesson import LessonStatus
from core.models import BaseModel


class LessonSession(BaseModel):
    """
    Represents the actual occurrence of a scheduled lesson.
    """

    timetable_entry = models.ForeignKey(
        TimetableEntry,
        on_delete=models.PROTECT,
        related_name="lesson_sessions",
    )

    lesson_date = models.DateField()

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lesson_sessions",
    )

    status = models.CharField(
        max_length=20,
        choices=LessonStatus.choices,
        default=LessonStatus.SCHEDULED,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "lesson_sessions"

        ordering = [
            "-lesson_date",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "timetable_entry",
                    "lesson_date",
                ],
                name="unique_lesson_session",
            )
        ]

    def __str__(self):
        return (
            f"{self.lesson_date} - "
            f"{self.timetable_entry}"
        )
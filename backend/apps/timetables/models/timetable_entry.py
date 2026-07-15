from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import Classroom
from apps.teachers.models import TeacherSubject
from core.constants.timetable import WeekDay
from core.models import BaseModel

from .period import Period
from .timetable import Timetable


class TimetableEntry(BaseModel):
    """
    Represents a single scheduled lesson within a timetable.
    """

    timetable = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE,
        related_name="entries",
    )

    weekday = models.CharField(
        max_length=20,
        choices=WeekDay.choices,
    )

    period = models.ForeignKey(
        Period,
        on_delete=models.PROTECT,
        related_name="timetable_entries",
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="timetable_entries",
    )

    teacher_subject = models.ForeignKey(
        TeacherSubject,
        on_delete=models.PROTECT,
        related_name="timetable_entries",
    )

    room = models.CharField(
        _("Room"),
        max_length=100,
        blank=True,
    )

    class Meta:
        db_table = "timetable_entries"

        ordering = [
            "weekday",
            "period__sequence",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "timetable",
                    "weekday",
                    "period",
                    "classroom",
                ],
                name="unique_classroom_period",
            ),
            models.UniqueConstraint(
                fields=[
                    "timetable",
                    "weekday",
                    "period",
                    "teacher_subject",
                ],
                name="unique_teacher_period",
            ),
        ]

    def __str__(self):
        return (
            f"{self.classroom} - "
            f"{self.weekday} "
            f"{self.period}"
        )
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.lessons.models import LessonSession
from core.constants.attendance import RegisterStatus
from core.models import BaseModel


class AttendanceRegister(BaseModel):
    """
    Attendance register for a lesson session.
    """

    lesson_session = models.OneToOneField(
        LessonSession,
        on_delete=models.PROTECT,
        related_name="attendance_register",
    )

    status = models.CharField(
        _("Register Status"),
        max_length=20,
        choices=RegisterStatus.choices,
        default=RegisterStatus.DRAFT,
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    locked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "attendance_registers"

        verbose_name = _("Attendance Register")
        verbose_name_plural = _("Attendance Registers")

    def __str__(self):
        return f"Attendance Register - {self.lesson_session}"
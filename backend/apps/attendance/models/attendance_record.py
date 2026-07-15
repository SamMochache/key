from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.enrollment.models import Enrollment
from core.constants.attendance import AttendanceStatus
from core.models import BaseModel

from .attendance_register import AttendanceRegister


class AttendanceRecord(BaseModel):
    """
    Attendance record for an enrolled student.
    """

    attendance_register = models.ForeignKey(
        AttendanceRegister,
        on_delete=models.CASCADE,
        related_name="records",
    )

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    status = models.CharField(
        _("Attendance Status"),
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "attendance_records"

        verbose_name = _("Attendance Record")
        verbose_name_plural = _("Attendance Records")

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "attendance_register",
                    "enrollment",
                ],
                name="unique_attendance_record",
            )
        ]

    def __str__(self):
        return (
            f"{self.enrollment.student} - "
            f"{self.status}"
        )
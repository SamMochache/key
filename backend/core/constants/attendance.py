from django.db import models
from django.utils.translation import gettext_lazy as _


class AttendanceStatus(models.TextChoices):
    """
    Student attendance status.
    """

    PRESENT = "PRESENT", _("Present")
    ABSENT = "ABSENT", _("Absent")
    LATE = "LATE", _("Late")
    EXCUSED = "EXCUSED", _("Excused")

class RegisterStatus(models.TextChoices):
    """
    Attendance register workflow.
    """

    DRAFT = "DRAFT", _("Draft")
    SUBMITTED = "SUBMITTED", _("Submitted")
    LOCKED = "LOCKED", _("Locked")
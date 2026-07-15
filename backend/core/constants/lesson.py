from django.db import models
from django.utils.translation import gettext_lazy as _


class LessonStatus(models.TextChoices):
    """
    Represents the outcome of a scheduled lesson.
    """

    SCHEDULED = "SCHEDULED", _("Scheduled")
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")
    COMPLETED = "COMPLETED", _("Completed")
    CANCELLED = "CANCELLED", _("Cancelled")
    MISSED = "MISSED", _("Missed")
from django.db import models
from django.utils.translation import gettext_lazy as _


class WeekDay(models.TextChoices):
    """
    Days of the academic week.
    """

    MONDAY = "MONDAY", _("Monday")
    TUESDAY = "TUESDAY", _("Tuesday")
    WEDNESDAY = "WEDNESDAY", _("Wednesday")
    THURSDAY = "THURSDAY", _("Thursday")
    FRIDAY = "FRIDAY", _("Friday")

class TimetableStatus(models.TextChoices):
    """
    Status of a timetable.
    """

    DRAFT = "DRAFT", _("Draft")
    PUBLISHED = "PUBLISHED", _("Published")
    ARCHIVED = "ARCHIVED", _("Archived")
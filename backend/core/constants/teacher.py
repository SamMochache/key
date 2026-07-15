from django.db import models
from django.utils.translation import gettext_lazy as _


class EmploymentType(models.TextChoices):
    """
    Types of teacher employment.
    """

    FULL_TIME = "FULL_TIME", _("Full Time")
    PART_TIME = "PART_TIME", _("Part Time")
    CONTRACT = "CONTRACT", _("Contract")
    INTERN = "INTERN", _("Intern")

class TeacherStatus(models.TextChoices):
    """
    Current employment status.
    """

    ACTIVE = "ACTIVE", _("Active")
    ON_LEAVE = "ON_LEAVE", _("On Leave")
    SUSPENDED = "SUSPENDED", _("Suspended")
    RESIGNED = "RESIGNED", _("Resigned")
    RETIRED = "RETIRED", _("Retired")
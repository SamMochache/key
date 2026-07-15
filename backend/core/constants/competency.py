from django.db import models
from django.utils.translation import gettext_lazy as _


class CompetencyLevel(models.TextChoices):
    """
    Represents a learner's mastery level for a competency.
    """

    BEGINNING = "BEGINNING", _("Beginning")
    DEVELOPING = "DEVELOPING", _("Developing")
    PROFICIENT = "PROFICIENT", _("Proficient")
    ADVANCED = "ADVANCED", _("Advanced")
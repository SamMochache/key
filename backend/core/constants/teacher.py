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

from django.db import models
from django.utils.translation import gettext_lazy as _


class QualificationType(models.TextChoices):
    """
    Types of professional qualifications.
    """

    DEGREE = "DEGREE", _("Degree")
    DIPLOMA = "DIPLOMA", _("Diploma")
    CERTIFICATE = "CERTIFICATE", _("Certificate")
    LICENSE = "LICENSE", _("Teaching License")
    TRAINING = "TRAINING", _("Professional Training")

from django.db import models
from django.utils.translation import gettext_lazy as _


class TeacherRole(models.TextChoices):
    """
    Teacher's role within a subject assignment.
    """

    LEAD = "LEAD", _("Lead Teacher")
    ASSISTANT = "ASSISTANT", _("Assistant Teacher")


from django.db import models
from django.utils.translation import gettext_lazy as _


class ClassroomRole(models.TextChoices):
    """
    Role of a teacher within a classroom.
    """

    HOMEROOM = "HOMEROOM", _("Homeroom Teacher")
    ASSISTANT = "ASSISTANT", _("Assistant Teacher")
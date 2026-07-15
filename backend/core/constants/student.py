from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    """
    Supported gender values.
    """

    MALE = "MALE", _("Male")
    FEMALE = "FEMALE", _("Female")


class StudentStatus(models.TextChoices):
    """
    Current enrollment status of a student.
    """

    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")
    GRADUATED = "GRADUATED", _("Graduated")
    TRANSFERRED = "TRANSFERRED", _("Transferred")
    WITHDRAWN = "WITHDRAWN", _("Withdrawn")

class GuardianRelationship(models.TextChoices):
    """
    Relationship between a guardian and a student.
    """

    FATHER = "FATHER", _("Father")
    MOTHER = "MOTHER", _("Mother")
    GUARDIAN = "GUARDIAN", _("Guardian")
    GRANDPARENT = "GRANDPARENT", _("Grandparent")
    UNCLE = "UNCLE", _("Uncle")
    AUNT = "AUNT", _("Aunt")
    SIBLING = "SIBLING", _("Sibling")
    OTHER = "OTHER", _("Other")

from django.db import models
from django.utils.translation import gettext_lazy as _


class BloodGroup(models.TextChoices):
    """
    Supported blood groups.
    """

    A_POSITIVE = "A+", _("A+")
    A_NEGATIVE = "A-", _("A-")
    B_POSITIVE = "B+", _("B+")
    B_NEGATIVE = "B-", _("B-")
    AB_POSITIVE = "AB+", _("AB+")
    AB_NEGATIVE = "AB-", _("AB-")
    O_POSITIVE = "O+", _("O+")
    O_NEGATIVE = "O-", _("O-")
    UNKNOWN = "UNKNOWN", _("Unknown")
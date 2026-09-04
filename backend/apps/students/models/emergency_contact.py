from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.student import EmergencyRelationship
from core.models import BaseModel

from .student import Student,Guardian


class EmergencyContact(BaseModel):
    """
    Emergency contacts for a student.
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )

    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emergency_contact_records",
    )

    full_name = models.CharField(
        _("Full Name"),
        max_length=200,
    )

    relationship = models.CharField(
        _("Relationship"),
        max_length=30,
        choices=EmergencyRelationship.choices,
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
    )

    alternative_phone_number = models.CharField(
        _("Alternative Phone Number"),
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        _("Email Address"),
        blank=True,
    )

    physical_address = models.TextField(
        _("Physical Address"),
        blank=True,
    )

    is_primary_contact = models.BooleanField(
        _("Primary Contact"),
        default=False,
    )

    can_pick_up_student = models.BooleanField(
        _("Authorized Pickup"),
        default=True,
    )

    notes = models.TextField(
        _("Notes"),
        blank=True,
    )

    class Meta:
        db_table = "emergency_contacts"
        verbose_name = _("Emergency Contact")
        verbose_name_plural = _("Emergency Contacts")
        ordering = [
            "-is_primary_contact",
            "full_name",
        ]

    def __str__(self):
        return (
            f"{self.full_name} "
            f"({self.student})"
        )
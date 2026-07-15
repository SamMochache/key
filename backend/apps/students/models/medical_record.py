from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.student import BloodGroup
from core.models import BaseModel

from .student import Student


class MedicalRecord(BaseModel):
    """
    Stores medical information for a student.
    """

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="medical_record",
    )

    blood_group = models.CharField(
        _("Blood Group"),
        max_length=10,
        choices=BloodGroup.choices,
        default=BloodGroup.UNKNOWN,
    )

    allergies = models.TextField(
        _("Allergies"),
        blank=True,
    )

    medical_conditions = models.TextField(
        _("Medical Conditions"),
        blank=True,
    )

    medications = models.TextField(
        _("Current Medications"),
        blank=True,
    )

    dietary_restrictions = models.TextField(
        _("Dietary Restrictions"),
        blank=True,
    )

    emergency_medical_notes = models.TextField(
        _("Emergency Medical Notes"),
        blank=True,
    )

    physician_name = models.CharField(
        _("Physician Name"),
        max_length=150,
        blank=True,
    )

    physician_phone = models.CharField(
        _("Physician Phone"),
        max_length=20,
        blank=True,
    )

    hospital = models.CharField(
        _("Preferred Hospital"),
        max_length=150,
        blank=True,
    )

    class Meta:
        db_table = "medical_records"
        verbose_name = _("Medical Record")
        verbose_name_plural = _("Medical Records")

    def __str__(self):
        return f"Medical Record - {self.student}"
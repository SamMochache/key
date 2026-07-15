from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.teacher import QualificationType
from core.models import BaseModel

from .teacher import Teacher


class Qualification(BaseModel):
    """
    Professional qualification held by a teacher.
    """

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="qualifications",
    )

    qualification_type = models.CharField(
        _("Qualification Type"),
        max_length=20,
        choices=QualificationType.choices,
    )

    title = models.CharField(
        _("Qualification"),
        max_length=200,
    )

    institution = models.CharField(
        _("Institution"),
        max_length=200,
    )

    date_awarded = models.DateField()

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    certificate = models.FileField(
        upload_to="teachers/qualifications/",
        blank=True,
        null=True,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_teacher_qualifications",
    )

    class Meta:
        db_table = "teacher_qualifications"

        verbose_name = _("Teacher Qualification")
        verbose_name_plural = _("Teacher Qualifications")

        ordering = [
            "-date_awarded",
        ]

    def __str__(self):
        return (
            f"{self.teacher} - "
            f"{self.title}"
        )
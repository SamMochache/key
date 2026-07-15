from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.identity.models import User
from apps.schools.models import School
from core.models import BaseModel
from core.constants.student import Gender


class Student(BaseModel):
    """
    Represents a student profile.

    Authentication and personal identity are handled
    by the associated User model.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="student_profile",
    )

    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name="students",
    )

    admission_number = models.CharField(
        _("Admission Number"),
        max_length=50,
    )

    admission_date = models.DateField()

    date_of_birth = models.DateField()

    gender = models.CharField(
        _("Gender"),
        max_length=10,
        choices=Gender.choices,
    )

    nationality = models.CharField(
        _("Nationality"),
        max_length=100,
        default="Kenyan",
    )

    birth_certificate_number = models.CharField(
        _("Birth Certificate Number"),
        max_length=50,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "students"
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
        ordering = ["admission_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "admission_number"],
                name="unique_student_admission_number_per_school",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.first_name} "
            f"{self.user.last_name}"
        )

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.student import GuardianRelationship
from core.models import BaseModel

from .guardian import Guardian
from .student import Student


class StudentGuardian(BaseModel):
    """
    Associates students with their guardians.
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_guardians",
    )

    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="guardian_students",
    )

    relationship = models.CharField(
        _("Relationship"),
        max_length=20,
        choices=GuardianRelationship.choices,
    )

    can_pick_up = models.BooleanField(
        default=True,
    )

    receives_notifications = models.BooleanField(
        default=True,
    )

    lives_with_student = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "student_guardians"

        constraints = [
            models.UniqueConstraint(
                fields=["student", "guardian"],
                name="unique_student_guardian",
            )
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.guardian}"
        )
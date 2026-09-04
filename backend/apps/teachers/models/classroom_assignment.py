from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import (
    AcademicYear,
    Classroom,
    Term,
)
from core.constants.teacher import ClassroomRole
from core.models import BaseModel

from .teacher import Teacher


class ClassroomAssignment(BaseModel):
    """
    Assigns a teacher to manage a classroom
    during an academic year and term.
    """

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="classroom_assignments",
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="classroom_assignments",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="classroom_assignments",
    )

    role = models.CharField(
        _("Assignment Role"),
        max_length=20,
        choices=ClassroomRole.choices,
        default=ClassroomRole.HOMEROOM,
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "classroom_assignments"

        verbose_name = _("Classroom Assignment")
        verbose_name_plural = _("Classroom Assignments")

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "classroom",
                    "academic_year",
                    "term",
                    "role",
                ],
                name="unique_classroom_teacher_assignment",
            )
        ]

    def __str__(self):
        return (
            f"{self.teacher} → {self.classroom}"
        )
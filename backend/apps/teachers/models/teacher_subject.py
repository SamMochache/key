from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import (
    AcademicYear,
    Classroom,
    Subject,
    Term,
)
from core.constants.teacher import TeacherRole
from core.models import BaseModel

from .teacher import Teacher


class TeacherSubject(BaseModel):
    """
    Assigns a teacher to teach a subject in a classroom
    during a specific academic year and term.
    """

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="subject_assignments",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="teacher_subjects",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="teacher_subjects",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="teacher_subjects",
    )

    role = models.CharField(
        _("Teacher Role"),
        max_length=20,
        choices=TeacherRole.choices,
        default=TeacherRole.LEAD,
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
        db_table = "teacher_subject_assignments"

        verbose_name = _("Teacher Subject Assignment")
        verbose_name_plural = _("Teacher Subject Assignments")

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "subject",
                    "classroom",
                    "academic_year",
                    "term",
                ],
                name="unique_teacher_subject_assignment",
            )
        ]

    def __str__(self):
        return (
            f"{self.teacher} - "
            f"{self.subject}"
        )
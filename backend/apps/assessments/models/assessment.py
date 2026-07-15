from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.lessons.models import LessonSession
from apps.teachers.models import Teacher
from core.constants.assessment import (
    AssessmentStatus,
    AssessmentType,
)
from core.models import BaseModel


class Assessment(BaseModel):
    """
    Academic activity created by a teacher.
    """

    lesson_session = models.ForeignKey(
        LessonSession,
        on_delete=models.PROTECT,
        related_name="assessments",
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="assessments",
    )

    title = models.CharField(
        _("Title"),
        max_length=255,
    )

    description = models.TextField()

    assessment_type = models.CharField(
        max_length=30,
        choices=AssessmentType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=AssessmentStatus.choices,
        default=AssessmentStatus.DRAFT,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    maximum_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    allow_resubmission = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "assessments"

        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.title
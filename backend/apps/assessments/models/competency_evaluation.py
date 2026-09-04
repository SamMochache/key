from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.competency import CompetencyLevel
from core.models import BaseModel

from .competency import Competency
from .evaluation import AssessmentEvaluation


class CompetencyEvaluation(BaseModel):
    """
    Evaluation of a learner against a competency.
    """

    evaluation = models.ForeignKey(
        AssessmentEvaluation,
        on_delete=models.CASCADE,
        related_name="competency_evaluations",
    )

    competency = models.ForeignKey(
        Competency,
        on_delete=models.PROTECT,
        related_name="evaluations",
    )

    level = models.CharField(
        max_length=20,
        choices=CompetencyLevel.choices,
    )

    teacher_comment = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "competency_evaluations"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "evaluation",
                    "competency",
                ],
                name="unique_competency_evaluation",
            )
        ]

    def __str__(self):
        return (
            f"{self.competency} - "
            f"{self.level}"
        )
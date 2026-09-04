from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .evaluation import AssessmentEvaluation
from .rubric_criterion import RubricCriterion


class CriterionScore(BaseModel):
    """
    Score awarded for an individual rubric criterion.
    """

    evaluation = models.ForeignKey(
        AssessmentEvaluation,
        on_delete=models.CASCADE,
        related_name="criterion_scores",
    )

    criterion = models.ForeignKey(
        RubricCriterion,
        on_delete=models.PROTECT,
        related_name="criterion_scores",
    )

    score = models.DecimalField(
        _("Score"),
        max_digits=5,
        decimal_places=2,
    )

    feedback = models.TextField(
        _("Criterion Feedback"),
        blank=True,
    )

    class Meta:
        db_table = "criterion_scores"

        verbose_name = _("Criterion Score")
        verbose_name_plural = _("Criterion Scores")

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "evaluation",
                    "criterion",
                ],
                name="unique_evaluation_criterion",
            )
        ]

    def __str__(self):
        return f"{self.criterion} - {self.score}"
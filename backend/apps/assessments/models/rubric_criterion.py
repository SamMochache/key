from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from .rubric import Rubric


class RubricCriterion(BaseModel):
    """
    Individual grading criterion within a rubric.
    """

    rubric = models.ForeignKey(
        Rubric,
        on_delete=models.CASCADE,
        related_name="criteria",
    )
    title = models.CharField(
        _("Criterion"),
        max_length=255,
    )
    description = models.TextField(
        blank=True,
    )
    maximum_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5,
    )
    sequence = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "rubric_criteria"
        ordering = [
            "sequence",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "rubric",
                    "sequence",
                ],
                name="unique_rubric_sequence",
            )
        ]

    def __str__(self):
        return self.title

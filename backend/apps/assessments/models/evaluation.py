from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .submission import AssessmentSubmission


class AssessmentEvaluation(BaseModel):
    """
    Overall evaluation of an assessment submission.
    """

    submission = models.OneToOneField(
        AssessmentSubmission,
        on_delete=models.CASCADE,
        related_name="evaluation",
    )

    total_score = models.DecimalField(
        _("Total Score"),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    percentage = models.DecimalField(
        _("Percentage"),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    narrative_feedback = models.TextField(
        _("Narrative Feedback"),
        blank=True,
    )

    published = models.BooleanField(
        default=False,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "assessment_evaluations"

        verbose_name = _("Assessment Evaluation")
        verbose_name_plural = _("Assessment Evaluations")

    def __str__(self):
        return f"Evaluation - {self.submission}"
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.report_generation import GenerationStatus
from core.models import BaseModel

from .report import Report


class ReportGeneration(BaseModel):
    """
    Stores every AI generation attempt for a learner report.
    """

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="generations",
    )

    model_name = models.CharField(
        _("LLM Model"),
        max_length=100,
    )

    prompt_version = models.CharField(
        _("Prompt Version"),
        max_length=50,
        default="v1",
    )

    status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
    )

    prompt = models.TextField()

    context = models.JSONField()

    response = models.TextField(
        blank=True,
    )

    input_tokens = models.PositiveIntegerField(
        default=0,
    )

    output_tokens = models.PositiveIntegerField(
        default=0,
    )

    total_tokens = models.PositiveIntegerField(
        default=0,
    )

    duration_ms = models.PositiveIntegerField(
        default=0,
    )

    error_message = models.TextField(
        blank=True,
    )

    generated_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "report_generations"

        ordering = [
            "-generated_at",
        ]

    def __str__(self):
        return (
            f"{self.report} - "
            f"{self.model_name}"
        )
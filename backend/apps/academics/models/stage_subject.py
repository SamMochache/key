from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .cambridge_stage import CambridgeStage
from .subject import Subject


class StageSubject(BaseModel):
    """
    Associates a subject with a Cambridge stage.
    """

    cambridge_stage = models.ForeignKey(
        CambridgeStage,
        on_delete=models.CASCADE,
        related_name="stage_subjects",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="stage_subjects",
    )

    weekly_lessons = models.PositiveSmallIntegerField(
        _("Weekly Lessons"),
        default=5,
    )

    is_core = models.BooleanField(
        _("Core Subject"),
        default=True,
    )

    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "stage_subjects"
        verbose_name = _("Stage Subject")
        verbose_name_plural = _("Stage Subjects")
        ordering = [
            "cambridge_stage",
            "display_order",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cambridge_stage",
                    "subject",
                ],
                name="unique_subject_per_stage",
            )
        ]

    def __str__(self):
        return (
            f"{self.cambridge_stage} - "
            f"{self.subject.name}"
        )
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .programme import Programme


class CambridgeStage(BaseModel):
    """
    Represents a stage/year within a Cambridge programme.
    """

    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name="stages",
    )

    name = models.CharField(
        _("Stage Name"),
        max_length=100,
    )

    stage_number = models.PositiveSmallIntegerField()

    display_order = models.PositiveSmallIntegerField()

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "cambridge_stages"
        verbose_name = _("Cambridge Stage")
        verbose_name_plural = _("Cambridge Stages")
        ordering = ["display_order"]

        constraints = [
            models.UniqueConstraint(
                fields=["programme", "stage_number"],
                name="unique_stage_per_programme",
            )
        ]

    def __str__(self):
        return f"{self.programme.name} - {self.name}"
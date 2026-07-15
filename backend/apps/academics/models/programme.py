from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .curriculum import Curriculum


class Programme(BaseModel):
    """
    Represents a programme within a curriculum.

    Example:
    - Cambridge Primary
    - Cambridge Lower Secondary
    - Cambridge Upper Secondary
    """

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="programmes",
    )

    name = models.CharField(
        _("Programme Name"),
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    display_order = models.PositiveSmallIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "programmes"
        verbose_name = _("Programme")
        verbose_name_plural = _("Programmes")
        ordering = ["display_order"]

        constraints = [
            models.UniqueConstraint(
                fields=["curriculum", "name"],
                name="unique_programme_per_curriculum",
            )
        ]

    def __str__(self):
        return self.name
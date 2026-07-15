from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class MontessoriLevel(BaseModel):
    """
    Represents a Montessori developmental level.
    """

    name = models.CharField(
        _("Level Name"),
        max_length=100,
        unique=True,
    )

    code = models.CharField(
        _("Level Code"),
        max_length=20,
        unique=True,
    )

    minimum_age = models.DecimalField(
        _("Minimum Age"),
        max_digits=4,
        decimal_places=1,
        help_text=_("Minimum recommended age in years."),
    )

    maximum_age = models.DecimalField(
        _("Maximum Age"),
        max_digits=4,
        decimal_places=1,
        help_text=_("Maximum recommended age in years."),
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "montessori_levels"
        verbose_name = _("Montessori Level")
        verbose_name_plural = _("Montessori Levels")
        ordering = ["display_order"]

        constraints = [
            models.UniqueConstraint(
                fields=["display_order"],
                name="unique_montessori_display_order",
            )
        ]

    def __str__(self):
        return self.name
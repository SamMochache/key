from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schools.models import School
from core.models import BaseModel


class Period(BaseModel):
    """
    Represents a reusable period in a school day.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name="periods",
    )

    name = models.CharField(
        _("Period Name"),
        max_length=50,
    )

    sequence = models.PositiveSmallIntegerField(
        _("Sequence"),
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_break = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "periods"

        ordering = [
            "sequence",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "sequence"],
                name="unique_period_sequence_per_school",
            ),
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_period_name_per_school",
            ),
        ]

    def __str__(self):
        return self.name
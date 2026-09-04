from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schools.models import School
from core.models import BaseModel


class Competency(BaseModel):
    """
    Defines a competency assessed by the school.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="competencies",
    )

    name = models.CharField(
        _("Competency"),
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    sequence = models.PositiveSmallIntegerField()

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "competencies"

        ordering = [
            "sequence",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "school",
                    "name",
                ],
                name="unique_school_competency",
            ),
            models.UniqueConstraint(
                fields=[
                    "school",
                    "sequence",
                ],
                name="unique_school_competency_sequence",
            ),
        ]

    def __str__(self):
        return self.name
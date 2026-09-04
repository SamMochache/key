from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .academic_year import AcademicYear


class Term(BaseModel):
    """
    Represents an academic term within an academic year.
    """

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="terms",
    )

    term_number = models.PositiveSmallIntegerField(
        _("Term Number"),
    )

    
    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "terms"
        verbose_name = _("Term")
        verbose_name_plural = _("Terms")
        ordering = ["start_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "term_number"],
                name="unique_term_per_academic_year",
            )
        ]

    def __str__(self):
        return f"{self.academic_year.name} - {self.name}"
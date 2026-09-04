from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schools.models import School
from core.models import BaseModel


class AcademicYear(BaseModel):
    """
    Represents an academic year within a school.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="academic_years",
    )

    name = models.CharField(
        _("Academic Year"),
        max_length=20,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "academic_years"
        verbose_name = _("Academic Year")
        verbose_name_plural = _("Academic Years")
        ordering = ["-start_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_academic_year_per_school",
            )
        ]

    def __str__(self):
        return self.name
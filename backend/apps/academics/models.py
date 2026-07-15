from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from apps.schools.models import School


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
        ordering = ["-start_date"]
        unique_together = ("school", "name")

    def __str__(self):
        return self.name
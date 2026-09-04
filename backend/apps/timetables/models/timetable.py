from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import AcademicYear, Term
from apps.schools.models import School
from core.constants.timetable import TimetableStatus
from core.models import BaseModel


class Timetable(BaseModel):
    """
    Represents a timetable for a specific academic year and term.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name="timetables",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="timetables",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="timetables",
    )

    name = models.CharField(
        _("Timetable Name"),
        max_length=100,
    )

    version = models.PositiveSmallIntegerField(
        default=1,
    )

    status = models.CharField(
        max_length=20,
        choices=TimetableStatus.choices,
        default=TimetableStatus.DRAFT,
    )

    effective_from = models.DateField()

    effective_to = models.DateField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "timetables"

        ordering = [
            "-academic_year",
            "-version",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "school",
                    "academic_year",
                    "term",
                    "version",
                ],
                name="unique_timetable_version",
            )
        ]

    def __str__(self):
        return (
            f"{self.name} (v{self.version})"
        )
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schools.models import School
from core.models import BaseModel

from .academic_year import AcademicYear
from .term import Term
from .cambridge_stage import CambridgeStage
from .montessori_level import MontessoriLevel


class Classroom(BaseModel):
    """
    Represents an academic classroom for a specific academic year and term.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classrooms",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="classrooms",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="classrooms",
    )

    cambridge_stage = models.ForeignKey(
        CambridgeStage,
        on_delete=models.PROTECT,
        related_name="classrooms",
    )

    montessori_level = models.ForeignKey(
        MontessoriLevel,
        on_delete=models.PROTECT,
        related_name="classrooms",
        null=True,
        blank=True,
    )

    name = models.CharField(
        _("Classroom Name"),
        max_length=100,
    )

    code = models.CharField(
        _("Classroom Code"),
        max_length=30,
    )

    capacity = models.PositiveSmallIntegerField(
        _("Maximum Capacity"),
        default=30,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "classrooms"
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")
        ordering = [
            "academic_year",
            "cambridge_stage",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "code"],
                name="unique_classroom_code_per_year",
            )
        ]

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.academic_year.name})"
        )

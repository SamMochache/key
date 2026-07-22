from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import AcademicYear, Term
from apps.enrollment.models import Enrollment
from core.constants.report import ReportStatus
from core.models import BaseModel


class Report(BaseModel):
    """
    Represents a learner's academic report for a specific academic term.
    """

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT,
        related_name="reports",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="reports",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="reports",
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="generated_reports",
    )

    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.DRAFT,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "reports"

        ordering = [
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "term",
                ],
                name="unique_student_term_report",
            ),
        ]

    def __str__(self):
        return (
            f"{self.enrollment.student} - "
            f"{self.term.name}"
        )
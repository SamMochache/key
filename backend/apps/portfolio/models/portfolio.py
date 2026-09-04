from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.students.models import Student
from core.models import BaseModel


class Portfolio(BaseModel):
    """
    Digital learning portfolio for a student.
    """

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="portfolio",
    )

    summary = models.TextField(
        _("Portfolio Summary"),
        blank=True,
    )

    class Meta: # type: ignore
        db_table = "portfolios"

        verbose_name = _("Portfolio")
        verbose_name_plural = _("Portfolios")

    def __str__(self):
        return f"{self.student}"
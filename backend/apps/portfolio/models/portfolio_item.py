from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.assessments.models import AssessmentSubmission
from apps.lessons.models import LessonSession
from core.constants.portfolio import PortfolioItemType
from core.models import BaseModel

from .portfolio import Portfolio


class PortfolioItem(BaseModel):
    """
    Individual learning evidence within a student's portfolio.
    """

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="items",
    )

    lesson_session = models.ForeignKey(
        LessonSession,
        on_delete=models.SET_NULL,
        related_name="portfolio_items",
        null=True,
        blank=True,
    )

    assessment_submission = models.ForeignKey(
        AssessmentSubmission,
        on_delete=models.SET_NULL,
        related_name="portfolio_items",
        null=True,
        blank=True,
    )

    item_type = models.CharField(
        max_length=30,
        choices=PortfolioItemType.choices,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    event_date = models.DateField()

    class Meta:
        db_table = "portfolio_items"

        ordering = [
            "-event_date",
        ]

    def __str__(self):
        return self.title
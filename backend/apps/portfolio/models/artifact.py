from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .portfolio_item import PortfolioItem


class Artifact(BaseModel):
    """
    Media attached to a portfolio item.
    """

    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name="artifacts",
    )

    file = models.FileField(
        upload_to="portfolio/artifacts/",
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        db_table = "portfolio_artifacts"

    def __str__(self):
        return self.caption or self.file.name
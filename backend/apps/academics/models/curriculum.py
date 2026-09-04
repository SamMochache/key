from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Curriculum(BaseModel):
    """
    Represents an educational curriculum offered by the school.
    """

    name = models.CharField(
        _("Curriculum Name"),
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    version = models.CharField(
        _("Version"),
        max_length=50,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "curricula"
        verbose_name = _("Curriculum")
        verbose_name_plural = _("Curricula")
        ordering = ["name"]

    def __str__(self):
        if self.version:
            return f"{self.name} ({self.version})"
        return self.name
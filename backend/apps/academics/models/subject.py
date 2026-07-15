from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .curriculum import Curriculum


class Subject(BaseModel):
    """
    Represents a subject offered within a curriculum.
    """

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="subjects",
    )

    name = models.CharField(
        _("Subject Name"),
        max_length=100,
    )

    code = models.CharField(
        _("Subject Code"),
        max_length=20,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    is_core = models.BooleanField(
        _("Core Subject"),
        default=True,
    )

    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
    )

    is_active = models.BooleanField(
        _("Active"),
        default=True,
    )

    class Meta:
        db_table = "subjects"
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        ordering = ["display_order", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["curriculum", "code"],
                name="unique_subject_code_per_curriculum",
            )
        ]

    def __str__(self):
        return self.name
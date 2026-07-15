from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schools.models import School
from core.models import BaseModel


class Department(BaseModel):
    """
    Represents an organizational department within a school.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name="departments",
    )

    name = models.CharField(
        _("Department Name"),
        max_length=100,
    )

    code = models.CharField(
        _("Department Code"),
        max_length=20,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "departments"

        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_department_name_per_school",
            ),
            models.UniqueConstraint(
                fields=["school", "code"],
                name="unique_department_code_per_school",
            ),
        ]

    def __str__(self):
        return self.name
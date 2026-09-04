from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from core.models import BaseModel


class Guardian(BaseModel):
    """
    Represents a parent or guardian.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="guardian_profile",
    )

    occupation = models.CharField(
        _("Occupation"),
        max_length=150,
        blank=True,
    )

    employer = models.CharField(
        _("Employer"),
        max_length=150,
        blank=True,
    )

    physical_address = models.TextField(
        _("Physical Address"),
        blank=True,
    )

    is_primary_contact = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "guardians"
        verbose_name = _("Guardian")
        verbose_name_plural = _("Guardians")

    def __str__(self):
        return (
            f"{self.user.first_name} "
            f"{self.user.last_name}"
        )
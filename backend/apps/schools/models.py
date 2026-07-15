from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class School(BaseModel):
    """
    Represents a school.

    Although the initial deployment is for Key International School,
    the model is designed to support future expansion.
    """

    name = models.CharField(
        _("School Name"),
        max_length=255,
    )

    short_name = models.CharField(
        _("Short Name"),
        max_length=50,
        unique=True,
    )

    email = models.EmailField(
        _("School Email"),
        blank=True,
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=30,
        blank=True,
    )

    website = models.URLField(
        _("Website"),
        blank=True,
    )

    logo = models.ImageField(
        _("Logo"),
        upload_to="schools/logos/",
        blank=True,
        null=True,
    )

    address = models.TextField(
        _("Address"),
        blank=True,
    )

    city = models.CharField(
        _("City"),
        max_length=100,
        blank=True,
    )

    country = models.CharField(
        _("Country"),
        max_length=100,
        default="Kenya",
    )

    timezone = models.CharField(
        _("Timezone"),
        max_length=100,
        default="Africa/Nairobi",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "schools"
        ordering = ["name"]
        verbose_name = _("School")
        verbose_name_plural = _("Schools")

    def __str__(self):
        return self.name
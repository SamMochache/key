from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.user import UserStatus
from core.models import IdentityBaseModel

from .managers import UserManager


class User(IdentityBaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for authentication and identity.

    This model stores authentication credentials and basic profile
    information only. Business-specific information belongs in
    dedicated domain models such as Student, Teacher, or Parent.
    """

    email = models.EmailField(
        _("Email Address"),
        unique=True,
    )

    first_name = models.CharField(
        _("First Name"),
        max_length=150,
    )

    last_name = models.CharField(
        _("Last Name"),
        max_length=150,
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
        blank=True,
    )

    profile_photo = models.ImageField(
        _("Profile Photo"),
        upload_to="users/profile_photos/",
        blank=True,
        null=True,
    )

    preferred_language = models.CharField(
        _("Preferred Language"),
        max_length=20,
        default="en",
    )

    timezone = models.CharField(
        _("Timezone"),
        max_length=100,
        default="Africa/Nairobi",
    )

    status = models.CharField(
        _("Account Status"),
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )

    is_active = models.BooleanField(
        _("Active"),
        default=True,
    )

    is_staff = models.BooleanField(
        _("Staff Status"),
        default=False,
        help_text=_("Designates whether the user can access the Django admin site."),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        """
        Returns the user's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def initials(self) -> str:
        """
        Returns the user's initials.
        """
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()
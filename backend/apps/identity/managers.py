from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Responsible for:
    - Normalizing email addresses.
    - Creating regular users.
    - Creating superusers.
    """

    use_in_migrations = True

    @staticmethod
    def _normalize_email(email: str) -> str:
        """
        Normalize an email address before storing it.

        - Removes leading/trailing whitespace.
        - Normalizes the domain using Django's implementation.
        - Converts the entire email to lowercase.
        """

        if not email:
            raise ValueError(_("The email address must be provided."))

        return BaseUserManager.normalize_email(email.strip()).lower()

    def _create_user(self, email: str, password: str, **extra_fields):
        """
        Internal helper used by create_user() and create_superuser().
        """

        email = self._normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_user(self, email: str, password=None, **extra_fields):
        """
        Create and return a regular user.
        """

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )

    def create_superuser(self, email: str, password: str, **extra_fields):
        """
        Create and return a superuser.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )
from django.db import models


class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    SUSPENDED = "SUSPENDED", "Suspended"
    INVITED = "INVITED", "Invited"
    ARCHIVED = "ARCHIVED", "Archived"
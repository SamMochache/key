from django.db import models
from django.utils.translation import gettext_lazy as _


class GenerationStatus(models.TextChoices):
    """
    Status of an AI report generation request.
    """

    PENDING = "PENDING", _("Pending")
    PROCESSING = "PROCESSING", _("Processing")
    COMPLETED = "COMPLETED", _("Completed")
    FAILED = "FAILED", _("Failed")

from django.db import models
from django.utils.translation import gettext_lazy as _


class ReportStatus(models.TextChoices):
    """
    Workflow status of a learner report.
    """

    DRAFT = "DRAFT", _("Draft")
    GENERATED = "GENERATED", _("Generated")
    REVIEWED = "REVIEWED", _("Reviewed")
    APPROVED = "APPROVED", _("Approved")
    PUBLISHED = "PUBLISHED", _("Published")
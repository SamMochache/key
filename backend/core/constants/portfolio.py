from django.db import models
from django.utils.translation import gettext_lazy as _


class PortfolioItemType(models.TextChoices):
    """
    Types of evidence stored in a learner portfolio.
    """

    PROJECT = "PROJECT", _("Project")
    ARTWORK = "ARTWORK", _("Artwork")
    PHOTO = "PHOTO", _("Photo")
    VIDEO = "VIDEO", _("Video")
    AUDIO = "AUDIO", _("Audio")
    CERTIFICATE = "CERTIFICATE", _("Certificate")
    OBSERVATION = "OBSERVATION", _("Observation")
    PRESENTATION = "PRESENTATION", _("Presentation")
    ASSESSMENT = "ASSESSMENT", _("Assessment Evidence")
    OTHER = "OTHER", _("Other")
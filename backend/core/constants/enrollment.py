from django.db import models
from django.utils.translation import gettext_lazy as _


class EnrollmentStatus(models.TextChoices):
    """
    Current enrollment status.
    """

    PENDING = "PENDING", _("Pending")
    ENROLLED = "ENROLLED", _("Enrolled")
    PROMOTED = "PROMOTED", _("Promoted")
    TRANSFERRED = "TRANSFERRED", _("Transferred")
    WITHDRAWN = "WITHDRAWN", _("Withdrawn")
    GRADUATED = "GRADUATED", _("Graduated")
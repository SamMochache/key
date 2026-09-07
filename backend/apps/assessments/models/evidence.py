from django.conf import settings
from django.db import models

from core.models import BaseModel

from .competency import Competency
from .submission import AssessmentSubmission


class Evidence(BaseModel):
    """A piece of learner work captured as evidence for an assessment submission."""

    class EvidenceType(models.TextChoices):
        DOCUMENT = "DOCUMENT", "Document"
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"
        LINK = "LINK", "Link"
        OBSERVATION = "OBSERVATION", "Observation"
        OTHER = "OTHER", "Other"

    submission = models.ForeignKey(
        AssessmentSubmission,
        on_delete=models.CASCADE,
        related_name="evidence",
    )
    competency = models.ForeignKey(
        Competency,
        on_delete=models.PROTECT,
        related_name="evidence",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    evidence_type = models.CharField(
        max_length=20,
        choices=EvidenceType.choices,
        default=EvidenceType.OTHER,
    )
    file = models.FileField(
        upload_to="assessments/evidence/",
        blank=True,
        null=True,
    )
    url = models.URLField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_assessment_evidence",
    )

    class Meta:
        db_table = "assessment_evidence"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.submission}"

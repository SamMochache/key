from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants.student import (
    DocumentStatus,
    DocumentType,
)
from core.models import BaseModel

from .student import Student


class StudentDocument(BaseModel):
    """
    Documents uploaded for a student.
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        _("Document Type"),
        max_length=50,
        choices=DocumentType.choices,
    )

    title = models.CharField(
        _("Title"),
        max_length=200,
    )

    file = models.FileField(
        upload_to="students/documents/",
    )

    status = models.CharField(
        _("Verification Status"),
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_student_documents",
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="verified_student_documents",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "student_documents"
        verbose_name = _("Student Document")
        verbose_name_plural = _("Student Documents")

        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.document_type}"
        )
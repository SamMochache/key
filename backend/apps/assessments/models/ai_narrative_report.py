from django.conf import settings
from django.db import models

from apps.academics.models import AcademicYear, Term
from apps.students.models import Student
from core.models import BaseModel


class AINarrativeReport(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        REVIEWED = "REVIEWED", "Reviewed"
        PUBLISHED = "PUBLISHED", "Published"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="ai_narrative_reports",
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="ai_narrative_reports",
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="ai_narrative_reports",
    )
    generated_content = models.JSONField(default=dict)
    edited_content = models.JSONField(default=dict, blank=True)
    source_data_snapshot = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="generated_ai_narrative_reports",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_ai_narrative_reports",
        null=True,
        blank=True,
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="published_ai_narrative_reports",
        null=True,
        blank=True,
    )
    model_used = models.CharField(max_length=100, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ai_narrative_reports"
        ordering = ["-generated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "academic_year", "term"],
                name="unique_ai_narrative_report_period",
            ),
        ]

    def __str__(self):
        return f"AI report - {self.student} - {self.academic_year} - Term {self.term.term_number}"

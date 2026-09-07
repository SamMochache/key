from django.conf import settings
from django.db import models

from core.models import BaseModel


class AINarrativeReportHistory(BaseModel):
    class Action(models.TextChoices):
        GENERATED = "GENERATED", "Generated"
        EDITED = "EDITED", "Edited"
        REVIEWED = "REVIEWED", "Reviewed"
        PUBLISHED = "PUBLISHED", "Published"

    report = models.ForeignKey(
        "assessments.AINarrativeReport",
        on_delete=models.PROTECT,
        related_name="history",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ai_narrative_report_history",
    )
    occurred_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    model_used = models.CharField(max_length=100, blank=True)
    narrative_snapshot = models.JSONField(default=dict)
    source_data_snapshot = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ai_narrative_report_history"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["report", "occurred_at"]),
            models.Index(fields=["action", "occurred_at"]),
        ]

    def __str__(self):
        return f"{self.action} - {self.report_id} - {self.occurred_at}"

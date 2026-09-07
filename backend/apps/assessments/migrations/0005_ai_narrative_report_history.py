import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0004_ai_narrative_report"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AINarrativeReportHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("action", models.CharField(choices=[("GENERATED", "Generated"), ("EDITED", "Edited"), ("REVIEWED", "Reviewed"), ("PUBLISHED", "Published")], max_length=20)),
                ("occurred_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(max_length=20)),
                ("model_used", models.CharField(blank=True, max_length=100)),
                ("narrative_snapshot", models.JSONField(default=dict)),
                ("source_data_snapshot", models.JSONField(default=dict)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ai_narrative_report_history", to=settings.AUTH_USER_MODEL)),
                ("report", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="history", to="assessments.ainarrativereport")),
            ],
            options={
                "db_table": "ai_narrative_report_history",
                "ordering": ["-occurred_at"],
            },
        ),
        migrations.AddIndex(
            model_name="ainarrativereporthistory",
            index=models.Index(fields=["report", "occurred_at"], name="ai_report_h_report_i_6c0d6b_idx"),
        ),
        migrations.AddIndex(
            model_name="ainarrativereporthistory",
            index=models.Index(fields=["action", "occurred_at"], name="ai_report_h_action__d2a5d1_idx"),
        ),
    ]

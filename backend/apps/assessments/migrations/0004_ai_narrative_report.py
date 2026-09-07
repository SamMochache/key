import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0003_merge_0002_evidence_0002_initial"),
        ("academics", "0003_academicyear_is_active"),
        ("students", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AINarrativeReport",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("generated_content", models.JSONField(default=dict)),
                ("edited_content", models.JSONField(blank=True, default=dict)),
                ("source_data_snapshot", models.JSONField(default=dict)),
                ("status", models.CharField(choices=[("DRAFT", "Draft"), ("REVIEWED", "Reviewed"), ("PUBLISHED", "Published")], default="DRAFT", max_length=20)),
                ("model_used", models.CharField(blank=True, max_length=100)),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ai_narrative_reports", to="academics.academicyear")),
                ("generated_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="generated_ai_narrative_reports", to=settings.AUTH_USER_MODEL)),
                ("published_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="published_ai_narrative_reports", to=settings.AUTH_USER_MODEL)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_ai_narrative_reports", to=settings.AUTH_USER_MODEL)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ai_narrative_reports", to="students.student")),
                ("term", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ai_narrative_reports", to="academics.term")),
            ],
            options={
                "db_table": "ai_narrative_reports",
                "ordering": ["-generated_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="ainarrativereport",
            constraint=models.UniqueConstraint(fields=("student", "academic_year", "term"), name="unique_ai_narrative_report_period"),
        ),
    ]

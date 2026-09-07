import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Evidence",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("evidence_type", models.CharField(choices=[("DOCUMENT", "Document"), ("IMAGE", "Image"), ("VIDEO", "Video"), ("LINK", "Link"), ("OBSERVATION", "Observation"), ("OTHER", "Other")], default="OTHER", max_length=20)),
                ("file", models.FileField(blank=True, null=True, upload_to="assessments/evidence/")),
                ("url", models.URLField(blank=True)),
                ("competency", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="evidence", to="assessments.competency")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_assessment_evidence", to=settings.AUTH_USER_MODEL)),
                ("submission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evidence", to="assessments.assessmentsubmission")),
            ],
            options={
                "db_table": "assessment_evidence",
                "ordering": ["-created_at"],
            },
        ),
    ]

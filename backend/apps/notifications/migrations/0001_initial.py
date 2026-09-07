import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("schools", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("notification_type", models.CharField(choices=[("MESSAGE", "Message"), ("ASSESSMENT", "Assessment"), ("REPORT", "Report"), ("CALENDAR", "Calendar"), ("TIMETABLE", "Timetable"), ("SYSTEM", "System")], default="SYSTEM", max_length=20)),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField(blank=True)),
                ("link", models.CharField(blank=True, max_length=300)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="notifications", to="schools.school")),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "notifications",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(model_name="notification", index=models.Index(fields=["recipient", "read_at", "created_at"], name="notif_recip_read_created_idx")),
        migrations.AddIndex(model_name="notification", index=models.Index(fields=["school", "created_at"], name="notif_school_created_idx")),
    ]

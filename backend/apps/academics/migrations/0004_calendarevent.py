from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0003_academicyear_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="CalendarEvent",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("title", models.CharField(max_length=160)),
                ("event_type", models.CharField(choices=[("ACADEMIC", "Academic"), ("HOLIDAY", "Holiday"), ("EXAMINATION", "Examination"), ("MEETING", "Meeting"), ("ACTIVITY", "Activity"), ("DEADLINE", "Deadline"), ("OTHER", "Other")], default="ACADEMIC", max_length=20)),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                ("all_day", models.BooleanField(default=False)),
                ("location", models.CharField(blank=True, max_length=160)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="calendar_events", to="academics.academicyear")),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="calendar_events", to="schools.school")),
                ("term", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="calendar_events", to="academics.term")),
            ],
            options={
                "db_table": "calendar_events",
                "ordering": ["start_at", "title"],
                "indexes": [
                    models.Index(fields=["school", "start_at"], name="calendar_ev_school__9d2f75_idx"),
                    models.Index(fields=["school", "academic_year", "term"], name="calendar_ev_school__0e8d8c_idx"),
                ],
            },
        ),
    ]

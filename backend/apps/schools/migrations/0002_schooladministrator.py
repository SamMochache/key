from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("schools", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SchoolAdministrator",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="administrators", to="schools.school")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="school_admin_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "School Administrator",
                "verbose_name_plural": "School Administrators",
                "db_table": "school_administrators",
                "ordering": ["school__name", "user__first_name", "user__last_name"],
            },
        ),
    ]

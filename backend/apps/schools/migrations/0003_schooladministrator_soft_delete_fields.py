from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("schools", "0002_schooladministrator"),
    ]

    operations = [
        migrations.AddField(
            model_name="schooladministrator",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="schooladministrator",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0002_classroom_teacher_assignment"),
    ]

    operations = [
        migrations.AddField(
            model_name="academicyear",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]

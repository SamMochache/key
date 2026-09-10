from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enrollment", "0002_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(
                fields=["classroom", "academic_year", "term", "status"],
                name="enroll_scope_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(
                fields=["student", "status"],
                name="enroll_student_status_idx",
            ),
        ),
    ]

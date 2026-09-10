from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0005_rename_calendar_ev_school__9d2f75_idx_calendar_ev_school__8b78fe_idx_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="classroomteacherassignment",
            index=models.Index(fields=["teacher", "is_active"], name="cta_teacher_active_idx"),
        ),
        migrations.AddIndex(
            model_name="classroomteacherassignment",
            index=models.Index(fields=["classroom", "is_active"], name="cta_class_active_idx"),
        ),
    ]

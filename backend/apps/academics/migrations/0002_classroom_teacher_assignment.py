import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0001_initial"),
        ("teachers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClassroomTeacherAssignment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("PRIMARY", "Class Teacher"),
                            ("ASSISTANT", "Assistant Teacher"),
                        ],
                        default="PRIMARY",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "classroom",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="teacher_assignments",
                        to="academics.classroom",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="classroom_assignments",
                        to="teachers.teacher",
                    ),
                ),
            ],
            options={
                "verbose_name": "Classroom Teacher Assignment",
                "verbose_name_plural": "Classroom Teacher Assignments",
                "db_table": "classroom_teacher_assignments",
            },
        ),
        migrations.AddConstraint(
            model_name="classroomteacherassignment",
            constraint=models.UniqueConstraint(
                fields=("classroom", "teacher", "role"),
                name="unique_classroom_teacher_role",
            ),
        ),
    ]

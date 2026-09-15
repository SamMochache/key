import uuid

import django.db.models.deletion
from django.db import migrations, models


CREATE_CLASSROOM_TEACHER_ASSIGNMENT_SQL = """
CREATE TABLE IF NOT EXISTS "classroom_teacher_assignments" (
    "id" uuid NOT NULL PRIMARY KEY,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL,
    "deleted_at" timestamp with time zone NULL,
    "is_deleted" boolean NOT NULL,
    "role" varchar(20) NOT NULL,
    "is_active" boolean NOT NULL,
    "classroom_id" uuid NOT NULL,
    "teacher_id" uuid NOT NULL
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'unique_classroom_teacher_role'
          AND conrelid = 'classroom_teacher_assignments'::regclass
    ) THEN
        ALTER TABLE "classroom_teacher_assignments"
        ADD CONSTRAINT "unique_classroom_teacher_role"
        UNIQUE ("classroom_id", "teacher_id", "role");
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'classroom_teacher_as_classroom_id_a3425bac_fk_classroom'
          AND conrelid = 'classroom_teacher_assignments'::regclass
    ) THEN
        ALTER TABLE "classroom_teacher_assignments"
        ADD CONSTRAINT "classroom_teacher_as_classroom_id_a3425bac_fk_classroom"
        FOREIGN KEY ("classroom_id") REFERENCES "classrooms" ("id")
        DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'classroom_teacher_as_teacher_id_9b90c59c_fk_teachers_'
          AND conrelid = 'classroom_teacher_assignments'::regclass
    ) THEN
        ALTER TABLE "classroom_teacher_assignments"
        ADD CONSTRAINT "classroom_teacher_as_teacher_id_9b90c59c_fk_teachers_"
        FOREIGN KEY ("teacher_id") REFERENCES "teachers" ("id")
        DEFERRABLE INITIALLY DEFERRED;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS "classroom_teacher_assignments_classroom_id_a3425bac"
ON "classroom_teacher_assignments" ("classroom_id");

CREATE INDEX IF NOT EXISTS "classroom_teacher_assignments_teacher_id_9b90c59c"
ON "classroom_teacher_assignments" ("teacher_id");
"""

DROP_CLASSROOM_TEACHER_ASSIGNMENT_SQL = """
DROP TABLE IF EXISTS "classroom_teacher_assignments" CASCADE;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0001_initial"),
        ("teachers", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    CREATE_CLASSROOM_TEACHER_ASSIGNMENT_SQL,
                    DROP_CLASSROOM_TEACHER_ASSIGNMENT_SQL,
                ),
            ],
            state_operations=[
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
            ],
        ),
    ]

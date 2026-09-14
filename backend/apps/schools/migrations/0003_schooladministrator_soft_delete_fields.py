from django.db import migrations


class Migration(migrations.Migration):
    """
    Historical repair migration.

    SchoolAdministrator inherits from BaseModel, whose SoftDeleteModel
    already provides deleted_at and is_deleted. Those fields are created
    with the SchoolAdministrator table in migration 0002.

    The original version of this migration attempted to add the same
    columns again, causing fresh database creation to fail with
    DuplicateColumn errors.

    This migration intentionally performs no database operations while
    retaining the migration number for migration-history compatibility.
    """

    dependencies = [
        ("schools", "0002_schooladministrator"),
    ]

    operations = []

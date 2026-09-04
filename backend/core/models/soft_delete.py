from django.db import models
from django.utils import timezone


class SoftDeleteModel(models.Model):

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_deleted = models.BooleanField(
        default=False,
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(update_fields=["deleted_at", "is_deleted"])

    def restore(self):
        self.deleted_at = None
        self.is_deleted = False
        self.save(update_fields=["deleted_at", "is_deleted"])
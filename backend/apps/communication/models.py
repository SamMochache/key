from django.conf import settings
from django.db import models

from apps.schools.models import School
from core.models import BaseModel


class CommunicationMessage(BaseModel):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="communication_messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sent_communication_messages")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="received_communication_messages")
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "communication_messages"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["school", "recipient", "sent_at"]),
            models.Index(fields=["school", "sender", "sent_at"]),
        ]

    @property
    def is_read(self):
        return self.read_at is not None

    def __str__(self):
        return f"{self.subject} — {self.sender} → {self.recipient}"

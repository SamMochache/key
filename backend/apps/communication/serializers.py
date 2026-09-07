from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.schools.models import School

from .models import CommunicationMessage

User = get_user_model()


class CommunicationMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)
    sender_email = serializers.EmailField(source="sender.email", read_only=True)
    recipient_email = serializers.EmailField(source="recipient.email", read_only=True)
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = CommunicationMessage
        fields = [
            "id", "school", "sender", "sender_name", "sender_email",
            "recipient", "recipient_name", "recipient_email", "subject", "body",
            "sent_at", "read_at", "is_read",
        ]
        read_only_fields = ["id", "sender", "sent_at", "read_at"]


class CommunicationContactSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email"]

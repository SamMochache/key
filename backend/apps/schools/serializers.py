from rest_framework import serializers

from .models import School


class SchoolSerializer(serializers.ModelSerializer):
    student_count = serializers.IntegerField(read_only=True)
    teacher_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "short_name",
            "email",
            "phone_number",
            "website",
            "logo",
            "address",
            "city",
            "country",
            "timezone",
            "is_active",
            "student_count",
            "teacher_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "student_count", "teacher_count", "created_at", "updated_at"]

    def validate_short_name(self, value):
        return value.strip()

    def validate_name(self, value):
        return value.strip()

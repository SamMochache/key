from datetime import date

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.assessments.permissions import get_user_school
from apps.identity.models import User

from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    initials = serializers.CharField(source="user.initials", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    age = serializers.SerializerMethodField()
    first_name = serializers.CharField(source="user.first_name", write_only=True, required=False)
    last_name = serializers.CharField(source="user.last_name", write_only=True, required=False)
    account_email = serializers.EmailField(source="user.email", write_only=True, required=False)
    phone_number = serializers.CharField(source="user.phone_number", write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = Student
        fields = (
            "id", "user", "full_name", "email", "initials", "school", "school_name",
            "admission_number", "admission_date", "date_of_birth", "age", "gender",
            "nationality", "birth_certificate_number", "is_active", "created_at", "updated_at",
            "first_name", "last_name", "account_email", "phone_number", "password",
        )
        read_only_fields = (
            "id", "user", "full_name", "email", "initials", "school_name", "age", "created_at", "updated_at",
        )

    def get_age(self, obj):
        today = timezone.localdate()
        born = obj.date_of_birth
        birthday_day = min(born.day, 28) if born.month == 2 and born.day == 29 else born.day
        birthday = date(today.year, born.month, birthday_day)
        age = today.year - born.year
        if birthday > today:
            age -= 1
        return age

    def validate(self, attrs):
        request = self.context.get("request")
        school = attrs.get("school") or getattr(self.instance, "school", None)
        admission_number = attrs.get("admission_number")

        if school is not None and request is not None:
            user = request.user
            user_school = get_user_school(user)
            if user_school is not None and user_school.pk != school.pk:
                raise serializers.ValidationError({"school": "You can only use your own institution."})
            if user_school is None and not (user.is_staff or user.is_superuser):
                raise serializers.ValidationError({"school": "Your account has no institution context."})

        if admission_number and school:
            qs = Student.objects.filter(school=school, admission_number=admission_number)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"admission_number": "This admission number is already used by this institution."}
                )

        if self.instance is None:
            required = ("first_name", "last_name", "account_email", "password")
            missing = [field for field in required if not attrs.get(field)]
            if missing:
                raise serializers.ValidationError({field: "This field is required when creating a student." for field in missing})
        else:
            user_data = attrs.get("user", {})
            if "account_email" in user_data:
                qs = User.objects.filter(email=user_data["account_email"])
                if qs.exclude(pk=self.instance.user_id).exists():
                    raise serializers.ValidationError({"account_email": "This email is already in use."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **user_data)
        return Student.objects.create(user=user, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        password = validated_data.pop("password", None)
        user = instance.user

        for field, value in user_data.items():
            setattr(user, field, value)
        if password:
            user.set_password(password)
        user.save()

        return super().update(instance, validated_data)

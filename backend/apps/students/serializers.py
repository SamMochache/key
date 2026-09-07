from datetime import date

from django.utils import timezone
from rest_framework import serializers

from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    initials = serializers.CharField(source="user.initials", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            "id", "user", "full_name", "email", "initials", "school", "school_name",
            "admission_number", "admission_date", "date_of_birth", "age", "gender",
            "nationality", "birth_certificate_number", "is_active", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "full_name", "email", "initials", "school_name", "age", "created_at", "updated_at",
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
            if not (user.is_staff or user.is_superuser):
                teacher_profile = getattr(user, "teacher_profile", None)
                student_profile = getattr(user, "student_profile", None)
                profile = teacher_profile or student_profile
                user_school = getattr(profile, "school", None)
                if user_school is None or user_school.pk != school.pk:
                    raise serializers.ValidationError({"school": "You can only use your own institution."})

        if admission_number and school:
            qs = Student.objects.filter(school=school, admission_number=admission_number)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"admission_number": "This admission number is already used by this institution."}
                )

        return attrs

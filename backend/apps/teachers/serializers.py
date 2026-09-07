from rest_framework import serializers

from .models.teacher import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    initials = serializers.CharField(source="user.initials", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Teacher
        fields = (
            "id", "user", "full_name", "email", "initials", "school", "school_name",
            "employee_number", "employment_type", "employment_date", "status",
            "department", "department_name", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "full_name", "email", "initials", "school_name", "department_name",
            "created_at", "updated_at",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        school = attrs.get("school") or getattr(self.instance, "school", None)
        employee_number = attrs.get("employee_number")

        if school is not None and request is not None:
            user = request.user
            if not (user.is_staff or user.is_superuser):
                profile = getattr(user, "teacher_profile", None) or getattr(user, "student_profile", None)
                user_school = getattr(profile, "school", None)
                if user_school is None or user_school.pk != school.pk:
                    raise serializers.ValidationError({"school": "You can only use your own institution."})

        if employee_number and school:
            qs = Teacher.objects.filter(school=school, employee_number=employee_number)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"employee_number": "This employee number is already used by this institution."})

        return attrs

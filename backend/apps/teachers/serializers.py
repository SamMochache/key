from django.db import transaction
from rest_framework import serializers

from apps.identity.models import User

from .models.department import Department
from .models.teacher import Teacher
from .models.teacher_subject import TeacherSubject


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "school", "name", "code", "description", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        school = attrs.get("school") or getattr(self.instance, "school", None)
        if request and not (request.user.is_staff or request.user.is_superuser):
            profile = getattr(request.user, "teacher_profile", None) or getattr(request.user, "student_profile", None)
            if not profile or profile.school_id != getattr(school, "pk", None):
                raise serializers.ValidationError({"school": "You can only use your own institution."})
        return attrs


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    initials = serializers.CharField(source="user.initials", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    account_email = serializers.EmailField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    is_active = serializers.BooleanField(source="user.is_active", required=False)

    class Meta:
        model = Teacher
        fields = (
            "id", "user", "full_name", "email", "initials", "school", "school_name",
            "employee_number", "employment_type", "employment_date", "status",
            "department", "department_name", "first_name", "last_name", "account_email",
            "phone_number", "password", "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "user", "full_name", "email", "initials", "school_name", "department_name", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        school = attrs.get("school") or getattr(self.instance, "school", None)
        department = attrs.get("department") or getattr(self.instance, "department", None)
        employee_number = attrs.get("employee_number")
        account_email = attrs.get("account_email")
        if school is not None and request is not None and not (request.user.is_staff or request.user.is_superuser):
            profile = getattr(request.user, "teacher_profile", None) or getattr(request.user, "student_profile", None)
            if not profile or profile.school_id != school.pk:
                raise serializers.ValidationError({"school": "You can only use your own institution."})
        if department and school and department.school_id != school.pk:
            raise serializers.ValidationError({"department": "Department must belong to the selected institution."})
        if employee_number and school:
            qs = Teacher.objects.filter(school=school, employee_number=employee_number)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"employee_number": "This employee number is already used by this institution."})
        if account_email:
            qs = User.objects.filter(email__iexact=account_email.strip())
            if self.instance:
                qs = qs.exclude(pk=self.instance.user_id)
            if qs.exists():
                raise serializers.ValidationError({"account_email": "This email address is already in use."})
        if not self.instance:
            missing = [f for f in ("first_name", "last_name", "account_email", "password") if not attrs.get(f)]
            if missing:
                raise serializers.ValidationError({f: "This field is required when creating a teacher." for f in missing})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        account_email = validated_data.pop("account_email")
        phone_number = validated_data.pop("phone_number", "")
        password = validated_data.pop("password")
        user = User.objects.create_user(email=account_email, password=password, first_name=first_name, last_name=last_name, phone_number=phone_number)
        validated_data["user"] = user
        return Teacher.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)
        account_email = validated_data.pop("account_email", None)
        phone_number = validated_data.pop("phone_number", None)
        password = validated_data.pop("password", None)
        user_data = validated_data.pop("user", {})
        user = instance.user
        if first_name is not None: user.first_name = first_name
        if last_name is not None: user.last_name = last_name
        if account_email is not None: user.email = account_email.strip().lower()
        if phone_number is not None: user.phone_number = phone_number
        if password: user.set_password(password)
        if "is_active" in user_data: user.is_active = user_data["is_active"]
        user.save()
        return super().update(instance, validated_data)


class TeacherSubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.user.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_number = serializers.IntegerField(source="term.term_number", read_only=True)

    class Meta:
        model = TeacherSubject
        fields = (
            "id", "teacher", "teacher_name", "subject", "subject_name", "classroom", "classroom_name",
            "academic_year", "academic_year_name", "term", "term_number", "role", "start_date", "end_date", "is_active",
        )
        read_only_fields = ("id", "teacher_name", "subject_name", "classroom_name", "academic_year_name", "term_number")

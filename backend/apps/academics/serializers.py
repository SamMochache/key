from rest_framework import serializers

from apps.teachers.models import Teacher

from .models import AcademicYear, CambridgeStage, Classroom, ClassroomTeacherAssignment, Curriculum, MontessoriLevel, Programme, StageSubject, Subject, Term


def _request_user_school(serializer):
    request = serializer.context.get("request")
    user = getattr(request, "user", None)
    school_admin_profile = getattr(user, "school_admin_profile", None)
    if school_admin_profile is not None and school_admin_profile.is_active:
        return school_admin_profile.school
    teacher_profile = getattr(user, "teacher_profile", None)
    if teacher_profile is not None:
        return teacher_profile.school
    student_profile = getattr(user, "student_profile", None)
    if student_profile is not None:
        return student_profile.school
    return None


def _is_platform_admin(serializer):
    request = serializer.context.get("request")
    user = getattr(request, "user", None)
    school_admin_profile = getattr(user, "school_admin_profile", None)
    return bool(user and (user.is_superuser or (user.is_staff and not school_admin_profile)))


class AcademicYearSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = AcademicYear
        fields = ["id", "school", "school_name", "name", "start_date", "end_date", "is_current", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "school_name", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        school = attrs.get("school", getattr(self.instance, "school", None))
        user_school = _request_user_school(self)
        if not _is_platform_admin(self) and user_school is not None and school is not None and school.id != user_school.id:
            raise serializers.ValidationError({"school": "Academic years must belong to your institution."})
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"end_date": "End date must be on or after the start date."})
        if attrs.get("is_current") and attrs.get("is_active") is False:
            raise serializers.ValidationError({"is_current": "An inactive academic year cannot be current."})
        return attrs


class TermSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = Term
        fields = ["id", "academic_year", "academic_year_name", "term_number", "start_date", "end_date", "is_current", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "academic_year_name", "created_at", "updated_at"]

    def validate(self, attrs):
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        user_school = _request_user_school(self)
        if not _is_platform_admin(self) and user_school is not None and academic_year is not None and academic_year.school_id != user_school.id:
            raise serializers.ValidationError({"academic_year": "Terms must belong to your institution."})
        if self.instance is None and academic_year and not academic_year.is_active:
            raise serializers.ValidationError({"academic_year": "Terms cannot be assigned to an inactive academic year."})
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"end_date": "End date must be on or after the start date."})
        if attrs.get("is_current") and attrs.get("is_active") is False:
            raise serializers.ValidationError({"is_current": "An inactive term cannot be current."})
        return attrs


class CurriculumSerializer(serializers.ModelSerializer):
    subject_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Curriculum
        fields = ["id", "name", "description", "version", "is_active", "subject_count", "created_at", "updated_at"]
        read_only_fields = ["id", "subject_count", "created_at", "updated_at"]


class ProgrammeSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source="curriculum.name", read_only=True)

    class Meta:
        model = Programme
        fields = ["id", "curriculum", "curriculum_name", "name", "description", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "curriculum_name", "created_at", "updated_at"]


class SubjectSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source="curriculum.name", read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "curriculum", "curriculum_name", "name", "code", "description", "is_core", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "curriculum_name", "created_at", "updated_at"]


class CambridgeStageSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source="programme.name", read_only=True)

    class Meta:
        model = CambridgeStage
        fields = ["id", "programme", "programme_name", "name", "stage_number", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "programme_name", "created_at", "updated_at"]


class MontessoriLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MontessoriLevel
        fields = ["id", "name", "code", "minimum_age", "maximum_age", "description", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class StageSubjectSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source="cambridge_stage.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = StageSubject
        fields = ["id", "cambridge_stage", "stage_name", "subject", "subject_name", "weekly_lessons", "is_core", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "stage_name", "subject_name", "created_at", "updated_at"]


class ClassroomSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
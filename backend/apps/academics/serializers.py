from rest_framework import serializers

from apps.teachers.models import Teacher

from .models import AcademicYear, CambridgeStage, Classroom, ClassroomTeacherAssignment, Curriculum, MontessoriLevel, Programme, StageSubject, Subject, Term


class AcademicYearSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = AcademicYear
        fields = ["id", "school", "school_name", "name", "start_date", "end_date", "is_current", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "school_name", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
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
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_number = serializers.IntegerField(source="term.term_number", read_only=True)
    term_name = serializers.SerializerMethodField()
    stage_name = serializers.CharField(source="cambridge_stage.name", read_only=True)
    montessori_level_name = serializers.CharField(source="montessori_level.name", read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    subject_count = serializers.IntegerField(read_only=True)
    primary_teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.select_related("user"), required=False, allow_null=True, write_only=True)
    primary_teacher_id = serializers.SerializerMethodField()
    primary_teacher_name = serializers.SerializerMethodField()

    def get_term_name(self, obj):
        return str(obj.term)

    def _primary_assignment(self, obj):
        return next((assignment for assignment in obj.teacher_assignments.all() if assignment.role == ClassroomTeacherAssignment.Role.PRIMARY and assignment.is_active), None)

    def get_primary_teacher_id(self, obj):
        assignment = self._primary_assignment(obj)
        return str(assignment.teacher_id) if assignment else None

    def get_primary_teacher_name(self, obj):
        assignment = self._primary_assignment(obj)
        return assignment.teacher.user.full_name if assignment else None

    def validate(self, attrs):
        school = attrs.get("school")
        if school is None and self.instance is not None:
            school = self.instance.school
        if school is None:
            user = self.context.get("request").user if self.context.get("request") else None
            teacher_profile = getattr(user, "teacher_profile", None)
            school = teacher_profile.school if teacher_profile else None
        teacher = attrs.get("primary_teacher")
        if teacher is not None and school is not None and teacher.school_id != school.id:
            raise serializers.ValidationError({"primary_teacher": "Teacher must belong to the same institution as the class."})
        if teacher is not None and teacher.status != "ACTIVE":
            raise serializers.ValidationError({"primary_teacher": "Only active teachers can be assigned as class teachers."})
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        term = attrs.get("term", getattr(self.instance, "term", None))
        stage = attrs.get("cambridge_stage", getattr(self.instance, "cambridge_stage", None))
        if academic_year and school and academic_year.school_id != school.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to the same institution."})
        if term and academic_year and term.academic_year_id != academic_year.id:
            raise serializers.ValidationError({"term": "Term must belong to the selected academic year."})
        if stage is not None and not stage.is_active:
            raise serializers.ValidationError({"cambridge_stage": "Only active Cambridge stages can be assigned to a class."})
        return attrs

    def create(self, validated_data):
        teacher = validated_data.pop("primary_teacher", None)
        classroom = Classroom.objects.create(**validated_data)
        if teacher is not None:
            ClassroomTeacherAssignment.objects.create(classroom=classroom, teacher=teacher, role=ClassroomTeacherAssignment.Role.PRIMARY)
        return classroom

    def update(self, instance, validated_data):
        teacher = validated_data.pop("primary_teacher", serializers.empty)
        classroom = super().update(instance, validated_data)
        if teacher is not serializers.empty:
            ClassroomTeacherAssignment.objects.filter(classroom=classroom, role=ClassroomTeacherAssignment.Role.PRIMARY, is_active=True).update(is_active=False)
            if teacher is not None:
                ClassroomTeacherAssignment.objects.update_or_create(classroom=classroom, teacher=teacher, role=ClassroomTeacherAssignment.Role.PRIMARY, defaults={"is_active": True})
        return classroom

    class Meta:
        model = Classroom
        fields = ["id", "school", "school_name", "academic_year", "academic_year_name", "term", "term_number", "term_name", "cambridge_stage", "stage_name", "montessori_level", "montessori_level_name", "name", "code", "capacity", "student_count", "subject_count", "primary_teacher", "primary_teacher_id", "primary_teacher_name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "school_name", "academic_year_name", "term_number", "term_name", "stage_name", "montessori_level_name", "student_count", "subject_count", "primary_teacher_id", "primary_teacher_name", "created_at", "updated_at"]

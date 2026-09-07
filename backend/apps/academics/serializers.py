from rest_framework import serializers

from .models import AcademicYear, CambridgeStage, Classroom, Curriculum, MontessoriLevel, StageSubject, Subject, Term


class AcademicYearSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = AcademicYear
        fields = ["id", "school", "school_name", "name", "start_date", "end_date", "is_current", "created_at", "updated_at"]
        read_only_fields = ["id", "school_name", "created_at", "updated_at"]


class TermSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = Term
        fields = ["id", "academic_year", "academic_year_name", "term_number", "start_date", "end_date", "is_current", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "academic_year_name", "created_at", "updated_at"]


class CurriculumSerializer(serializers.ModelSerializer):
    subject_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Curriculum
        fields = ["id", "name", "description", "version", "is_active", "subject_count", "created_at", "updated_at"]
        read_only_fields = ["id", "subject_count", "created_at", "updated_at"]


class SubjectSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source="curriculum.name", read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "curriculum", "curriculum_name", "name", "code", "description", "is_core", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "curriculum_name", "created_at", "updated_at"]


class CambridgeStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CambridgeStage
        fields = ["id", "name", "code", "description", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MontessoriLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MontessoriLevel
        fields = ["id", "name", "code", "description", "display_order", "is_active", "created_at", "updated_at"]
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
    term_name = serializers.CharField(source="term.__str__", read_only=True)
    stage_name = serializers.CharField(source="cambridge_stage.name", read_only=True)
    montessori_level_name = serializers.CharField(source="montessori_level.name", read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    subject_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Classroom
        fields = [
            "id", "school", "school_name", "academic_year", "academic_year_name",
            "term", "term_number", "term_name", "cambridge_stage", "stage_name",
            "montessori_level", "montessori_level_name", "name", "code", "capacity",
            "student_count", "subject_count", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "school_name", "academic_year_name", "term_number", "term_name",
            "stage_name", "montessori_level_name", "student_count", "subject_count",
            "created_at", "updated_at",
        ]

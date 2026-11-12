from django.db import transaction
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
    student_count = serializers.IntegerField(read_only=True)
    subject_count = serializers.IntegerField(read_only=True)
    primary_teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.select_related("user").all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    primary_teacher_id = serializers.SerializerMethodField()
    primary_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = [
            "id", "school", "school_name", "academic_year", "term", "cambridge_stage",
            "montessori_level", "name", "code", "capacity", "is_active", "student_count",
            "subject_count", "primary_teacher", "primary_teacher_id", "primary_teacher_name",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "school_name", "student_count", "subject_count", "primary_teacher_id",
            "primary_teacher_name", "created_at", "updated_at",
        ]

    def _primary_assignment(self, classroom):
        assignments = getattr(classroom, "_prefetched_objects_cache", {}).get("teacher_assignments")
        if assignments is not None:
            return next(
                (
                    assignment for assignment in assignments
                    if assignment.role == ClassroomTeacherAssignment.Role.PRIMARY and assignment.is_active
                ),
                None,
            )
        return classroom.teacher_assignments.filter(
            role=ClassroomTeacherAssignment.Role.PRIMARY,
            is_active=True,
        ).select_related("teacher__user").first()

    def get_primary_teacher_id(self, classroom):
        assignment = self._primary_assignment(classroom)
        return str(assignment.teacher_id) if assignment else None

    def get_primary_teacher_name(self, classroom):
        assignment = self._primary_assignment(classroom)
        return assignment.teacher.user.full_name if assignment else None

    def validate(self, attrs):
        school = attrs.get("school", getattr(self.instance, "school", None))
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        term = attrs.get("term", getattr(self.instance, "term", None))
        primary_teacher = attrs.get("primary_teacher")
        user_school = _request_user_school(self)
        if school is None and not _is_platform_admin(self):
            school = user_school
        if not _is_platform_admin(self) and user_school is not None and school is not None and school.id != user_school.id:
            raise serializers.ValidationError({"school": "Classrooms must belong to your institution."})
        if academic_year is not None and school is not None and academic_year.school_id != school.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to the selected institution."})
        if term is not None and academic_year is not None and term.academic_year_id != academic_year.id:
            raise serializers.ValidationError({"term": "Term must belong to the selected academic year."})
        if attrs.get("capacity", getattr(self.instance, "capacity", 30)) <= 0:
            raise serializers.ValidationError({"capacity": "Capacity must be greater than zero."})
        if primary_teacher is not None:
            if school is None or primary_teacher.school_id != school.id:
                raise serializers.ValidationError({
                    "primary_teacher": "The class teacher must belong to the same institution as the classroom."
                })
            if primary_teacher.status != "ACTIVE" or not primary_teacher.user.is_active:
                raise serializers.ValidationError({
                    "primary_teacher": "Only active teacher accounts can be assigned to a classroom."
                })
        return attrs

    @staticmethod
    def _sync_primary_teacher(classroom, teacher):
        assignments = ClassroomTeacherAssignment.objects.filter(
            classroom=classroom,
            role=ClassroomTeacherAssignment.Role.PRIMARY,
        )
        if teacher is None:
            assignments.filter(is_active=True).update(is_active=False)
            getattr(classroom, "_prefetched_objects_cache", {}).pop("teacher_assignments", None)
            return

        # Deactivate the previous class teacher before activating the selected one.
        # The unique constraint includes inactive rows, so reuse an existing row
        # when the same teacher is assigned again instead of creating a duplicate.
        assignments.exclude(teacher=teacher).filter(is_active=True).update(is_active=False)
        assignment, _ = assignments.get_or_create(
            teacher=teacher,
            defaults={
                "classroom": classroom,
                "teacher": teacher,
                "role": ClassroomTeacherAssignment.Role.PRIMARY,
                "is_active": True,
            },
        )
        if not assignment.is_active:
            assignment.is_active = True
            assignment.save(update_fields=["is_active", "updated_at"])
        # The viewset prefetches assignments; invalidate that cache so the
        # response serializer reflects the just-saved relationship.
        getattr(classroom, "_prefetched_objects_cache", {}).pop("teacher_assignments", None)

    @transaction.atomic
    def create(self, validated_data):
        primary_teacher = validated_data.pop("primary_teacher", None)
        classroom = super().create(validated_data)
        self._sync_primary_teacher(classroom, primary_teacher)
        return classroom

    @transaction.atomic
    def update(self, instance, validated_data):
        primary_teacher = validated_data.pop("primary_teacher", serializers.empty)
        classroom = super().update(instance, validated_data)
        if primary_teacher is not serializers.empty:
            self._sync_primary_teacher(classroom, primary_teacher)
        return classroom

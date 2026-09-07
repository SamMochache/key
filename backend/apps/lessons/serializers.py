from rest_framework import serializers

from .models import LessonSession


class LessonSessionSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    term_number = serializers.IntegerField(source="term.term_number", read_only=True)

    class Meta:
        model = LessonSession
        fields = [
            "id", "classroom", "classroom_name", "subject", "subject_name",
            "teacher", "teacher_name", "term", "term_number", "title",
            "description", "lesson_date", "start_time", "end_time", "status",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "classroom_name", "subject_name", "teacher_name", "term_number", "created_at", "updated_at"]

    def validate(self, attrs):
        classroom = attrs.get("classroom", getattr(self.instance, "classroom", None))
        subject = attrs.get("subject", getattr(self.instance, "subject", None))
        teacher = attrs.get("teacher", getattr(self.instance, "teacher", None))
        term = attrs.get("term", getattr(self.instance, "term", None))
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        date = attrs.get("lesson_date", getattr(self.instance, "lesson_date", None))

        if not all([classroom, subject, teacher, term]):
            return attrs
        if classroom.term_id != term.id:
            raise serializers.ValidationError({"term": "Term must match the classroom term."})
        if classroom.academic_year_id != term.academic_year_id:
            raise serializers.ValidationError({"term": "Term must belong to the classroom academic year."})
        if subject.curriculum_id != classroom.cambridge_stage.programme.curriculum_id:
            raise serializers.ValidationError({"subject": "Subject must belong to the classroom curriculum."})
        if teacher.teacher_profile.school_id != classroom.school_id:
            raise serializers.ValidationError({"teacher": "Teacher must belong to the same institution as the classroom."})
        if not teacher.is_active:
            raise serializers.ValidationError({"teacher": "Only active teachers can teach lessons."})
        if start and end and start >= end:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})
        if date and date < term.start_date:
            raise serializers.ValidationError({"lesson_date": "Lesson date cannot be before the term starts."})
        if date and date > term.end_date:
            raise serializers.ValidationError({"lesson_date": "Lesson date cannot be after the term ends."})
        return attrs

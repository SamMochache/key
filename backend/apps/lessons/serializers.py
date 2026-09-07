from rest_framework import serializers

from .models import LessonSession


class LessonSessionSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(source="timetable_entry.classroom", read_only=True)
    classroom_name = serializers.CharField(source="timetable_entry.classroom.name", read_only=True)
    subject = serializers.PrimaryKeyRelatedField(source="timetable_entry.teacher_subject.subject", read_only=True)
    subject_name = serializers.CharField(source="timetable_entry.teacher_subject.subject.name", read_only=True)
    term = serializers.PrimaryKeyRelatedField(source="timetable_entry.timetable.term", read_only=True)
    term_number = serializers.IntegerField(source="timetable_entry.timetable.term.term_number", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    weekday = serializers.CharField(source="timetable_entry.weekday", read_only=True)
    start_time = serializers.TimeField(source="timetable_entry.period.start_time", read_only=True)
    end_time = serializers.TimeField(source="timetable_entry.period.end_time", read_only=True)
    room = serializers.CharField(source="timetable_entry.room", read_only=True)

    class Meta:
        model = LessonSession
        fields = [
            "id", "timetable_entry", "classroom", "classroom_name", "subject", "subject_name",
            "teacher", "teacher_name", "term", "term_number", "weekday", "start_time", "end_time",
            "room", "lesson_date", "started_at", "ended_at", "status", "remarks", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "classroom", "classroom_name", "subject", "subject_name", "teacher_name", "term",
            "term_number", "weekday", "start_time", "end_time", "room", "created_at", "updated_at",
        ]

    def validate(self, attrs):
        entry = attrs.get("timetable_entry", getattr(self.instance, "timetable_entry", None))
        teacher = attrs.get("teacher", getattr(self.instance, "teacher", None))
        date = attrs.get("lesson_date", getattr(self.instance, "lesson_date", None))
        if not entry or not teacher or not date:
            return attrs
        teacher_profile = getattr(teacher, "teacher_profile", None)
        if teacher_profile is None or entry.classroom.school_id != teacher_profile.school_id:
            raise serializers.ValidationError({"teacher": "Teacher must belong to the same institution as the classroom."})
        if not teacher.is_active or teacher_profile.status != "ACTIVE":
            raise serializers.ValidationError({"teacher": "Only active teachers can teach lessons."})
        if entry.teacher_subject.teacher.user_id != teacher.id:
            raise serializers.ValidationError({"teacher": "Teacher must match the teacher assigned to the timetable entry."})
        term = entry.timetable.term
        if date < term.start_date or date > term.end_date:
            raise serializers.ValidationError({"lesson_date": "Lesson date must fall within the timetable term."})
        return attrs

from rest_framework import serializers

from apps.academics.models import AcademicYear, Classroom, Term
from apps.schools.models import School
from apps.teachers.models import TeacherSubject

from .models.period import Period
from .models.timetable import Timetable
from .models.timetable_entry import TimetableEntry


class PeriodSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Period
        fields = (
            "id", "school", "school_name", "name", "sequence",
            "start_time", "end_time", "is_break", "created_at", "updated_at",
        )
        read_only_fields = ("id", "school_name", "created_at", "updated_at")

    def validate(self, attrs):
        if attrs.get("start_time") and attrs.get("end_time") and attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})
        return attrs


class TimetableSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_number = serializers.IntegerField(source="term.term_number", read_only=True)
    entry_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Timetable
        fields = (
            "id", "school", "school_name", "academic_year", "academic_year_name",
            "term", "term_number", "name", "version", "status", "effective_from",
            "effective_to", "entry_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "school_name", "academic_year_name", "term_number", "entry_count", "created_at", "updated_at")

    def validate(self, attrs):
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        term = attrs.get("term", getattr(self.instance, "term", None))
        school = attrs.get("school", getattr(self.instance, "school", None))
        if academic_year and term and term.academic_year_id != academic_year.id:
            raise serializers.ValidationError({"term": "Term must belong to the selected academic year."})
        if academic_year and school and academic_year.school_id != school.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to the selected institution."})
        if term and school and term.academic_year.school_id != school.id:
            raise serializers.ValidationError({"term": "Term must belong to the selected institution."})
        effective_from = attrs.get("effective_from", getattr(self.instance, "effective_from", None))
        effective_to = attrs.get("effective_to", getattr(self.instance, "effective_to", None))
        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError({"effective_to": "Effective end date cannot be before the start date."})
        if self.instance and self.instance.status == "PUBLISHED" and attrs.get("status") not in (None, "PUBLISHED"):
            raise serializers.ValidationError({"status": "Published timetables cannot be changed back to another status."})
        return attrs


class TimetableEntrySerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    subject_name = serializers.CharField(source="teacher_subject.subject.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher_subject.teacher.user.full_name", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)
    start_time = serializers.TimeField(source="period.start_time", read_only=True)
    end_time = serializers.TimeField(source="period.end_time", read_only=True)
    is_break = serializers.BooleanField(source="period.is_break", read_only=True)

    class Meta:
        model = TimetableEntry
        fields = (
            "id", "timetable", "weekday", "period", "period_name", "start_time", "end_time",
            "is_break", "classroom", "classroom_name", "teacher_subject", "subject_name",
            "teacher_name", "room", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "period_name", "start_time", "end_time", "is_break", "classroom_name",
            "subject_name", "teacher_name", "created_at", "updated_at",
        )

    def validate(self, attrs):
        timetable = attrs.get("timetable", getattr(self.instance, "timetable", None))
        period = attrs.get("period", getattr(self.instance, "period", None))
        classroom = attrs.get("classroom", getattr(self.instance, "classroom", None))
        assignment = attrs.get("teacher_subject", getattr(self.instance, "teacher_subject", None))
        if not timetable or not period or not classroom or not assignment:
            return attrs
        if timetable.status == "PUBLISHED":
            raise serializers.ValidationError("Published timetables are read-only. Create a new version to make changes.")
        if period.school_id != timetable.school_id:
            raise serializers.ValidationError({"period": "Period must belong to the timetable's institution."})
        if classroom.school_id != timetable.school_id:
            raise serializers.ValidationError({"classroom": "Classroom must belong to the timetable's institution."})
        if classroom.academic_year_id != timetable.academic_year_id or classroom.term_id != timetable.term_id:
            raise serializers.ValidationError({"classroom": "Classroom must belong to the timetable's academic period."})
        if assignment.classroom_id != classroom.id or assignment.academic_year_id != timetable.academic_year_id or assignment.term_id != timetable.term_id:
            raise serializers.ValidationError({"teacher_subject": "Teacher assignment must match the selected classroom and academic period."})
        if assignment.teacher.school_id != timetable.school_id or not assignment.is_active:
            raise serializers.ValidationError({"teacher_subject": "Teacher assignment must be active and belong to the timetable's institution."})
        return attrs

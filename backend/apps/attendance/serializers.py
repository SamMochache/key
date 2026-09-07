from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.enrollment.models import Enrollment
from apps.lessons.models import LessonSession
from core.constants.attendance import AttendanceStatus, RegisterStatus

from .models.attendance_record import AttendanceRecord
from .models.attendance_register import AttendanceRegister


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = serializers.UUIDField(source="enrollment.student_id", read_only=True)
    student_name = serializers.SerializerMethodField()
    admission_number = serializers.CharField(source="enrollment.student.admission_number", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ("id", "student", "student_name", "admission_number", "enrollment", "status", "remarks", "created_at", "updated_at")
        read_only_fields = ("id", "student", "student_name", "admission_number", "created_at", "updated_at")

    def get_student_name(self, obj):
        user = obj.enrollment.student.user
        return f"{user.first_name} {user.last_name}".strip() or user.email


class AttendanceRegisterSerializer(serializers.ModelSerializer):
    lesson_session = serializers.UUIDField(source="lesson_session_id", read_only=True)
    classroom = serializers.UUIDField(source="lesson_session.timetable_entry.classroom_id", read_only=True)
    classroom_name = serializers.CharField(source="lesson_session.timetable_entry.classroom.name", read_only=True)
    subject_name = serializers.CharField(source="lesson_session.timetable_entry.teacher_subject.subject.name", read_only=True)
    lesson_date = serializers.DateField(source="lesson_session.lesson_date", read_only=True)
    records = AttendanceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = AttendanceRegister
        fields = ("id", "lesson_session", "classroom", "classroom_name", "subject_name", "lesson_date", "status", "submitted_at", "locked_at", "records", "created_at", "updated_at")
        read_only_fields = fields


class AttendanceBulkItemSerializer(serializers.Serializer):
    enrollment = serializers.UUIDField()
    status = serializers.ChoiceField(choices=AttendanceStatus.choices)
    remarks = serializers.CharField(required=False, allow_blank=True)


class AttendanceBulkSerializer(serializers.Serializer):
    lesson_session = serializers.UUIDField()
    records = AttendanceBulkItemSerializer(many=True, allow_empty=False)
    submit = serializers.BooleanField(default=False)

    def validate(self, attrs):
        lesson = LessonSession.objects.select_related(
            "timetable_entry__classroom",
            "timetable_entry__teacher_subject__subject",
            "timetable_entry__timetable",
        ).filter(pk=attrs["lesson_session"]).first()
        if lesson is None:
            raise serializers.ValidationError({"lesson_session": "Lesson session not found."})
        if lesson.status not in (LessonSession.Status.IN_PROGRESS, LessonSession.Status.COMPLETED):
            raise serializers.ValidationError({"lesson_session": "Attendance can only be recorded for an active or completed lesson."})
        attrs["lesson"] = lesson
        ids = [item["enrollment"] for item in attrs["records"]]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError({"records": "Each enrollment may appear only once."})
        valid = set(Enrollment.objects.filter(
            id__in=ids,
            classroom_id=lesson.timetable_entry.classroom_id,
            term_id=lesson.timetable_entry.timetable.term_id,
            status="ENROLLED",
        ).values_list("id", flat=True))
        if any(item not in valid for item in ids):
            raise serializers.ValidationError({"records": "Every student must be actively enrolled in this lesson's class and term."})
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        attrs = self.validated_data
        lesson = attrs["lesson"]
        register, _ = AttendanceRegister.objects.select_for_update().get_or_create(lesson_session=lesson)
        if register.status == RegisterStatus.LOCKED:
            raise serializers.ValidationError("This attendance register is locked.")
        for item in attrs["records"]:
            AttendanceRecord.objects.update_or_create(
                attendance_register=register,
                enrollment_id=item["enrollment"],
                defaults={"status": item["status"], "remarks": item.get("remarks", "")},
            )
        if attrs.get("submit"):
            register.status = RegisterStatus.SUBMITTED
            register.submitted_at = timezone.now()
            register.save(update_fields=["status", "submitted_at", "updated_at"])
        return register

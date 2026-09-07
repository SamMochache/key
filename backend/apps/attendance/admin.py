from django.contrib import admin

from .models.attendance_record import AttendanceRecord
from .models.attendance_register import AttendanceRegister


@admin.register(AttendanceRegister)
class AttendanceRegisterAdmin(admin.ModelAdmin):
    list_display = ("lesson_session", "status", "submitted_at", "locked_at")
    list_filter = ("status",)
    search_fields = (
        "lesson_session__timetable_entry__classroom__name",
        "lesson_session__timetable_entry__teacher_subject__subject__name",
        "lesson_session__teacher__email",
    )
    autocomplete_fields = ("lesson_session",)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "attendance_register", "status")
    list_filter = ("status",)
    search_fields = (
        "enrollment__student__user__first_name",
        "enrollment__student__user__last_name",
        "enrollment__student__admission_number",
    )
    autocomplete_fields = ("attendance_register", "enrollment")

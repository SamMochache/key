from django.contrib import admin

from .models import LessonSession


@admin.register(LessonSession)
class LessonSessionAdmin(admin.ModelAdmin):
    list_display = (
        "lesson_date",
        "classroom_name",
        "subject_name",
        "teacher",
        "start_time",
        "status",
    )
    list_filter = (
        "status",
        "lesson_date",
        "teacher",
    )
    search_fields = (
        "teacher__first_name",
        "teacher__last_name",
        "teacher__email",
        "timetable_entry__classroom__name",
        "timetable_entry__teacher_subject__subject__name",
    )
    ordering = (
        "-lesson_date",
        "timetable_entry__period__start_time",
    )
    autocomplete_fields = (
        "timetable_entry",
        "teacher",
    )

    @admin.display(description="Class", ordering="timetable_entry__classroom__name")
    def classroom_name(self, obj):
        return obj.timetable_entry.classroom.name

    @admin.display(
        description="Subject",
        ordering="timetable_entry__teacher_subject__subject__name",
    )
    def subject_name(self, obj):
        return obj.timetable_entry.teacher_subject.subject.name

    @admin.display(description="Start time", ordering="timetable_entry__period__start_time")
    def start_time(self, obj):
        return obj.timetable_entry.period.start_time

from django.contrib import admin

from .models import TimetableEntry


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = (
        "timetable",
        "weekday",
        "period",
        "classroom",
        "teacher_subject",
        "room",
    )
    list_filter = (
        "weekday",
        "timetable",
        "period",
        "classroom",
    )
    search_fields = (
        "classroom__name",
        "teacher_subject__teacher__user__first_name",
        "teacher_subject__teacher__user__last_name",
        "teacher_subject__subject__name",
        "room",
    )
    autocomplete_fields = (
        "timetable",
        "period",
        "classroom",
        "teacher_subject",
    )

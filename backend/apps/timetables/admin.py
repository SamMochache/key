from django.contrib import admin

from apps.teachers.models.teacher_subject import TeacherSubject

from .models.period import Period
from .models.timetable import Timetable
from .models.timetable_entry import TimetableEntry


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "school",
        "sequence",
        "start_time",
        "end_time",
        "is_break",
    )
    list_filter = (
        "school",
        "is_break",
    )
    search_fields = (
        "name",
        "school__name",
    )
    ordering = (
        "school",
        "sequence",
    )


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "school",
        "academic_year",
        "term",

    )
    list_filter = (
        "school",
        "academic_year",
        "term",
    
    )
    search_fields = (
        "name",
        "school__name",
    )


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "subject",
        "classroom",
        "academic_year",
        "term",
        "role",
        "is_active",
    )
    list_filter = (
        "academic_year",
        "term",
        "role",
        "is_active",
    )
    search_fields = (
        "subject__name",
        "classroom__name",
    )


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
        "teacher_subject__subject__name",
        "room",
    )
    autocomplete_fields = (
        "timetable",
        "period",
        "classroom",
        "teacher_subject",
    )
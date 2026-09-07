from django.contrib import admin

from .models import LessonSession


@admin.register(LessonSession)
class LessonSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "classroom", "subject", "teacher", "lesson_date", "start_time", "status")
    list_filter = ("status", "term", "subject", "lesson_date")
    search_fields = ("title", "description", "classroom__name", "subject__name", "teacher__first_name", "teacher__last_name")
    ordering = ("-lesson_date", "-start_time")

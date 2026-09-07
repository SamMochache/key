from django.contrib import admin

from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "classroom",
        "academic_year",
        "term",
        "status",
        "enrollment_date",
    )
    list_filter = ("status", "academic_year", "term", "classroom")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
        "classroom__name",
    )
    ordering = ("-academic_year", "student")

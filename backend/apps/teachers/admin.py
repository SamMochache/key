from django.contrib import admin

from .models.department import Department
from .models.teacher import Teacher


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "school",
        "is_active",
        "created_at",
    )
    search_fields = (
        "name",
        "code",
        "school__name",
        "school__short_name",
    )
    list_filter = (
        "is_active",
        "school",
    )
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("school", "name")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "full_name_display",
        "employee_number",
        "school",
        "department",
        "employment_type",
        "status",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "employee_number",
        "school__name",
    )
    list_filter = (
        "school",
        "department",
        "employment_type",
        "status",
    )
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("school", "user__last_name", "user__first_name")

    @admin.display(description="Teacher", ordering="user__last_name")
    def full_name_display(self, obj):
        return obj.user.full_name

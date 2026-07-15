from django.contrib import admin

from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "country",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "short_name",
        "email",
    )

    list_filter = (
        "country",
        "is_active",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = ("name",)

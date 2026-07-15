from .models import MedicalRecord
from django.contrib import admin


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "blood_group",
        "physician_name",
    )

    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "physician_name",
    )

    list_filter = (
        "blood_group",
    )
from .models import MedicalRecord,StudentDocument
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


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "document_type",
        "status",
        "uploaded_by",
        "verified_by",
        "created_at",
    )

    list_filter = (
        "document_type",
        "status",
    )

    search_fields = (
        "student__admission_number",
        "title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
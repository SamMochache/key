from django.contrib import admin

from .models import MedicalRecord, Student, StudentDocument


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name_display",
        "admission_number",
        "school",
        "gender",
        "nationality",
        "is_active",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "admission_number",
    )
    list_filter = (
        "school",
        "gender",
        "nationality",
        "is_active",
    )
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("school", "admission_number")

    @admin.display(description="Student", ordering="user__last_name")
    def full_name_display(self, obj):
        return obj.user.full_name


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
    list_filter = ("blood_group",)


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

from django.contrib import admin

from .models import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "evidence_type",
        "student_name",
        "assessment_title",
        "competency",
        "created_by",
        "created_at",
    )
    list_filter = ("evidence_type", "created_at", "competency")
    search_fields = (
        "title",
        "description",
        "submission__enrollment__student__user__first_name",
        "submission__enrollment__student__user__last_name",
        "submission__assessment__title",
    )
    autocomplete_fields = ("submission", "competency", "created_by")

    @admin.display(description="Student")
    def student_name(self, obj):
        return obj.submission.enrollment.student.user.full_name

    @admin.display(description="Assessment")
    def assessment_title(self, obj):
        return obj.submission.assessment.title

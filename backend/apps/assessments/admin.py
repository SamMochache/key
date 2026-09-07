from django.contrib import admin

from .models import AINarrativeReport, AINarrativeReportHistory, Evidence


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

    @admin.display(description="Student")
    def student_name(self, obj):
        return obj.submission.enrollment.student.user.full_name

    @admin.display(description="Assessment")
    def assessment_title(self, obj):
        return obj.submission.assessment.title


@admin.register(AINarrativeReport)
class AINarrativeReportAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "academic_year",
        "term",
        "status",
        "generated_by",
        "reviewed_by",
        "published_by",
        "generated_at",
        "published_at",
    )
    list_filter = ("status", "academic_year", "term")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
    )
    readonly_fields = ("generated_at", "reviewed_at", "published_at")


@admin.register(AINarrativeReportHistory)
class AINarrativeReportHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "report",
        "action",
        "actor",
        "status",
        "model_used",
        "occurred_at",
    )
    list_filter = ("action", "status", "occurred_at")
    search_fields = (
        "report__student__user__first_name",
        "report__student__user__last_name",
        "actor__first_name",
        "actor__last_name",
        "actor__email",
    )
    readonly_fields = (
        "report",
        "action",
        "actor",
        "occurred_at",
        "status",
        "model_used",
        "narrative_snapshot",
        "source_data_snapshot",
        "metadata",
    )

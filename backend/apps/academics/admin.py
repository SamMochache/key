from django.contrib import admin

from .models import AcademicYear, Curriculum, Term, MontessoriLevel, Subject, StageSubject


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "version",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "version",
    )

    list_filter = (
        "is_active",
    )

    ordering = ("name",)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "school",
        "start_date",
        "end_date",
        "is_current",
    )

    list_filter = (
        "school",
        "is_current",
    )

    search_fields = (
        "name",
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "term_number",
        "academic_year",
        "start_date",
        "end_date",
        "is_current",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "is_current",
        "is_active",
    )

    ordering = (
        "academic_year",
        "term_number",
    )


@admin.register(MontessoriLevel)
class MontessoriLevelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "minimum_age",
        "maximum_age",
        "display_order",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )

    ordering = (
        "display_order",
    )

    list_filter = (
        "is_active",
    )


from .models import CambridgeStage, Programme


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "curriculum",
        "display_order",
        "is_active",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "curriculum",
        "is_active",
    )

    ordering = (
        "display_order",
    )


@admin.register(CambridgeStage)
class CambridgeStageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "programme",
        "stage_number",
        "display_order",
        "is_active",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "programme",
        "is_active",
    )

    ordering = (
        "programme",
        "display_order",
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "curriculum",
        "is_core",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "curriculum",
        "is_core",
        "is_active",
    )

    ordering = (
        "display_order",
        "name",
    )


@admin.register(StageSubject)
class StageSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "cambridge_stage",
        "subject",
        "weekly_lessons",
        "is_core",
        "display_order",
    )

    list_filter = (
        "cambridge_stage",
        "is_core",
    )

    search_fields = (
        "subject__name",
    )

    ordering = (
        "cambridge_stage",
        "display_order",
    )

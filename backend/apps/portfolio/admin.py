from django.contrib import admin

from .models import Artifact, Portfolio, PortfolioItem


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("student", "item_count", "created_at", "updated_at")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__email",
        "student__admission_number",
    )

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "portfolio", "item_type", "event_date", "created_at")
    list_filter = ("item_type", "event_date")
    search_fields = ("title", "description", "portfolio__student__user__first_name", "portfolio__student__user__last_name")
    autocomplete_fields = ("portfolio", "lesson_session", "assessment_submission")


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ("caption", "portfolio_item", "created_at")
    search_fields = ("caption", "portfolio_item__title")
    autocomplete_fields = ("portfolio_item",)

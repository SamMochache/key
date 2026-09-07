from django.contrib import admin

from .models import Parent, ParentStudentRelationship


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("full_name_display", "email_display", "school", "is_active")
    search_fields = ("user__first_name", "user__last_name", "user__email")
    list_filter = ("school", "is_active")

    @admin.display(description="Parent")
    def full_name_display(self, obj):
        return obj.user.full_name

    @admin.display(description="Email")
    def email_display(self, obj):
        return obj.user.email


@admin.register(ParentStudentRelationship)
class ParentStudentRelationshipAdmin(admin.ModelAdmin):
    list_display = ("parent", "student", "relationship", "can_view_reports", "is_primary_contact", "is_active")
    list_filter = ("relationship", "can_view_reports", "is_primary_contact", "is_active")
    search_fields = ("parent__user__first_name", "parent__user__last_name", "student__user__first_name", "student__user__last_name", "student__admission_number")

from django import forms
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class UserCreationForm(forms.ModelForm):
    """Create a User with a properly hashed password."""

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        strip=False,
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "preferred_language",
            "timezone",
            "status",
            "is_active",
            "is_staff",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Edit a User without exposing or overwriting the stored password hash."""

    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Passwords are stored as hashes. Use the password-change link "
            "to set a new password."
        ),
    )

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "email",
        "full_name_display",
        "role_display",
        "is_staff",
        "is_active",
        "status",
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "status",
    )
    ordering = ("first_name", "last_name", "email")
    readonly_fields = ("id", "created_at", "updated_at", "password")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "profile_photo",
                )
            },
        ),
        (
            "Preferences",
            {"fields": ("preferred_language", "timezone")},
        ),
        (
            "Account",
            {"fields": ("status", "is_active", "is_staff")},
        ),
        (
            "Permissions",
            {"fields": ("groups", "user_permissions")},
        ),
        (
            "Metadata",
            {"fields": ("id", "created_at", "updated_at")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "status",
                ),
            },
        ),
    )

    @admin.display(description="Name", ordering="first_name")
    def full_name_display(self, obj):
        return obj.full_name

    @admin.display(description="Role")
    def role_display(self, obj):
        if obj.is_superuser or obj.is_staff:
            return "Admin"
        if hasattr(obj, "teacher_profile"):
            return "Teacher"
        if hasattr(obj, "student_profile"):
            return "Student"
        return "User"

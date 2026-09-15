from rest_framework.permissions import BasePermission


class IsPlatformAdmin(BasePermission):
    message = "Platform administrator access is required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            (user.is_staff or user.is_superuser)
            and getattr(user, "school_admin_profile", None) is None
        )

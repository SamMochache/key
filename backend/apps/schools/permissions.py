from rest_framework import permissions


class SchoolAccessPermission(permissions.BasePermission):
    """School tenancy rules for administrators, staff, students, and parents."""

    message = "You do not have permission to access this institution."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return self._user_school(request.user) is not None or self._is_admin(request.user)
        return self._is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if self._is_admin(request.user):
            return True
        return request.method in permissions.SAFE_METHODS and self._user_school(request.user) == obj

    @staticmethod
    def _is_admin(user):
        return bool(user.is_staff or user.is_superuser)

    @staticmethod
    def _user_school(user):
        for relation in ("teacher_profile", "student_profile", "parent_profile"):
            profile = getattr(user, relation, None)
            if profile is not None:
                return profile.school
        return None

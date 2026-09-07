from rest_framework import permissions


class SchoolAccessPermission(permissions.BasePermission):
    """
    School tenancy rules:
    - Administrators can manage every school.
    - Teachers and students can only read their own school.
    - Non-admin users cannot create, modify, or delete schools.
    """

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
        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile is not None:
            return teacher_profile.school

        student_profile = getattr(user, "student_profile", None)
        if student_profile is not None:
            return student_profile.school

        return None

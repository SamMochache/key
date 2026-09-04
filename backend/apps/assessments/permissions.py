from rest_framework.permissions import BasePermission


class UserRole:
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    USER = "user"


def get_user_role(user):
    """Resolve the application role from the user's profile relationships."""
    if not user or not user.is_authenticated:
        return UserRole.USER
    if user.is_superuser or user.is_staff:
        return UserRole.ADMIN
    if hasattr(user, "teacher_profile"):
        return UserRole.TEACHER
    if hasattr(user, "student_profile"):
        return UserRole.STUDENT
    return UserRole.USER


def get_user_school(user):
    """Return the school associated with a teacher/student, otherwise None."""
    role = get_user_role(user)
    if role == UserRole.TEACHER:
        return user.teacher_profile.school
    if role == UserRole.STUDENT:
        return user.student_profile.school
    return None


class AdminOnly(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) == UserRole.ADMIN


class TeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) in {UserRole.ADMIN, UserRole.TEACHER}


class AssessmentAccessPermission(BasePermission):
    """Teachers/admins manage assessments; students may only read them."""

    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if role == UserRole.ADMIN or role == UserRole.TEACHER:
            return True
        return role == UserRole.STUDENT and request.method in {"GET", "HEAD", "OPTIONS"}


class SubmissionAccessPermission(BasePermission):
    """Teachers/admins manage submissions; students create/update their own."""

    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if role in {UserRole.ADMIN, UserRole.TEACHER}:
            return True
        return role == UserRole.STUDENT and request.method in {
            "GET", "POST", "PUT", "PATCH", "HEAD", "OPTIONS"
        }


class EvaluationAccessPermission(BasePermission):
    """Only teachers/admins can create, edit, or publish evaluations."""

    def has_permission(self, request, view):
        return get_user_role(request.user) in {UserRole.ADMIN, UserRole.TEACHER}

from rest_framework.permissions import BasePermission

from apps.academics.models import ClassroomTeacherAssignment


class UserRole:
    ADMIN = "admin"
    TEACHER = "teacher"
    PARENT = "parent"
    STUDENT = "student"
    USER = "user"


def get_user_role(user):
    """Resolve the application role from the user's profile relationships."""
    if not user or not user.is_authenticated:
        return UserRole.USER
    school_admin = getattr(user, "school_admin_profile", None)
    if school_admin is not None and school_admin.is_active:
        return UserRole.ADMIN
    if user.is_superuser or user.is_staff:
        return UserRole.ADMIN
    if hasattr(user, "teacher_profile"):
        return UserRole.TEACHER
    if hasattr(user, "parent_profile"):
        return UserRole.PARENT
    if hasattr(user, "student_profile"):
        return UserRole.STUDENT
    return UserRole.USER


def get_user_school(user):
    """Return the institution associated with an institution-scoped user.

    Platform staff/superusers intentionally have no single school context; an
    institution administrator resolves through ``school_admin_profile``.
    """
    school_admin = getattr(user, "school_admin_profile", None)
    if school_admin is not None and school_admin.is_active:
        return school_admin.school
    role = get_user_role(user)
    if role == UserRole.TEACHER:
        return user.teacher_profile.school
    if role == UserRole.PARENT:
        return user.parent_profile.school
    if role == UserRole.STUDENT:
        return user.student_profile.school
    return None


def is_platform_admin(user):
    """Return True only for unrestricted platform administrators."""
    return bool(
        user
        and user.is_authenticated
        and user.is_superuser
        or (
            user
            and user.is_authenticated
            and user.is_staff
            and getattr(user, "school_admin_profile", None) is None
            and getattr(user, "teacher_profile", None) is None
            and getattr(user, "parent_profile", None) is None
            and getattr(user, "student_profile", None) is None
        )
    )


def teacher_can_access_classroom(user, classroom_id):
    """Return whether a teacher has an active assignment to a classroom."""
    if get_user_role(user) != UserRole.TEACHER:
        return False
    teacher = getattr(user, "teacher_profile", None)
    if teacher is None:
        return False
    return ClassroomTeacherAssignment.objects.filter(
        teacher_id=teacher.id,
        classroom_id=classroom_id,
        is_active=True,
    ).exists()


def teacher_can_access_enrollment(user, enrollment):
    """Return whether a teacher is assigned to the enrollment's classroom.

    Classrooms are already scoped to an academic year and term, so checking the
    active classroom assignment also enforces the correct academic period.
    """
    if get_user_role(user) != UserRole.TEACHER:
        return False
    classroom_id = getattr(enrollment, "classroom_id", None)
    return classroom_id is not None and teacher_can_access_classroom(user, classroom_id)


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
        if role in {UserRole.ADMIN, UserRole.TEACHER}:
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

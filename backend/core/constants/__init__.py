from .student import Gender, StudentStatus
from .user import UserStatus
from .enrollment import EnrollmentStatus
from .timetable import TimetableStatus
from .teacher import TeacherStatus
from .lesson import LessonStatus
from .attendance import AttendanceStatus,RegisterStatus


__all__ = [
    "Gender",
    "StudentStatus",
    "UserStatus",
    "EnrollmentStatus",
    "TimetableStatus",
    "TeacherStatus"
    "LessonStatus",
    "AttendanceStatus"
    "RegisterStatus"
]
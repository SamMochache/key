from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AttendanceContext:
    """
    Attendance summary used by AI report generation.
    """

    total_school_days: int

    days_present: int

    days_absent: int

    days_late: int

    attendance_percentage: float
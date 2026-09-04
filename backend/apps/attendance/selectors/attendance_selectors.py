from django.db.models import Count, Q

from apps.ai_reports.dto import AttendanceContext
from apps.attendance.models import Attendance


class AttendanceSelectors:
    """
    Read-only queries for attendance.
    """

    def build_context(
        self,
        enrollment,
    ) -> AttendanceContext:

        queryset = Attendance.objects.filter(
            enrollment=enrollment,
        )

        summary = queryset.aggregate(
            total=Count("id"),
            present=Count(
                "id",
                filter=Q(status="PRESENT"),
            ),
            absent=Count(
                "id",
                filter=Q(status="ABSENT"),
            ),
            late=Count(
                "id",
                filter=Q(status="LATE"),
            ),
        )

        total = summary["total"] or 0

        present = summary["present"] or 0

        absent = summary["absent"] or 0

        late = summary["late"] or 0

        percentage = (
            (present / total) * 100
            if total
            else 0.0
        )

        return AttendanceContext(
            total_school_days=total,
            days_present=present,
            days_absent=absent,
            days_late=late,
            attendance_percentage=round(
                percentage,
                2,
            ),
        )
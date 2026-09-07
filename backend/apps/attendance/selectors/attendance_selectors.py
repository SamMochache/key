from django.db.models import Count, Q

from apps.ai_reports.dto import AttendanceContext

from ..models.attendance_record import AttendanceRecord


class AttendanceSelectors:
    """Read-only attendance queries used by reporting."""

    def build_context(self, enrollment):
        queryset = AttendanceRecord.objects.filter(enrollment=enrollment)
        summary = queryset.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="PRESENT")),
            absent=Count("id", filter=Q(status="ABSENT")),
            late=Count("id", filter=Q(status="LATE")),
        )
        total = summary["total"] or 0
        present = summary["present"] or 0
        return AttendanceContext(
            total_school_days=total,
            days_present=present,
            days_absent=summary["absent"] or 0,
            days_late=summary["late"] or 0,
            attendance_percentage=round((present / total) * 100, 2) if total else 0.0,
        )

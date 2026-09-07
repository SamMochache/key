from django.http import JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.assessments.models import AINarrativeReportHistory
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.enrollment.models import Enrollment


def _staff_school(request):
    role = get_user_role(request.user)
    if role not in {UserRole.ADMIN, UserRole.TEACHER}:
        raise PermissionDenied("Only staff can access AI report history.")
    return get_user_school(request.user)


class AINarrativeReportHistoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        school = _staff_school(request)
        report_id = request.query_params.get("report")
        if not report_id:
            return JsonResponse({"detail": "Report id is required."}, status=400)

        history = AINarrativeReportHistory.objects.select_related("actor", "report").filter(report_id=report_id)
        if school is not None:
            history = history.filter(
                report__student__enrollments__classroom__school_id=school.id,
                report__student__enrollments__academic_year_id=request.query_params.get("academic_year", history.first().report.academic_year_id if history.exists() else None),
                report__student__enrollments__term_id=request.query_params.get("term", history.first().report.term_id if history.exists() else None),
            ).distinct()

        results = []
        for item in history[:100]:
            results.append({
                "id": str(item.id),
                "action": item.action,
                "status": item.status,
                "actor": {
                    "id": str(item.actor_id),
                    "name": item.actor.get_full_name() or item.actor.email,
                },
                "occurred_at": item.occurred_at,
                "model": item.model_used,
                "narrative": item.narrative_snapshot,
                "source_data": item.source_data_snapshot,
                "metadata": item.metadata,
            })
        return JsonResponse({"results": results})

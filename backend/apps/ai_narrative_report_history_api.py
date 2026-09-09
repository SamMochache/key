from django.http import JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.assessments.models import AINarrativeReport, AINarrativeReportHistory
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

        report = AINarrativeReport.objects.filter(id=report_id).first()
        if report is None:
            return JsonResponse({"detail": "Report not found."}, status=404)

        if school is not None and not Enrollment.objects.filter(
            student_id=report.student_id,
            academic_year_id=report.academic_year_id,
            term_id=report.term_id,
            classroom__school_id=school.id,
        ).exists():
            raise PermissionDenied("The report does not belong to your institution.")

        history = AINarrativeReportHistory.objects.select_related("actor").filter(report_id=report.id)
        results = []
        for item in history[:100]:
            actor = item.actor
            actor_name = getattr(actor, "full_name", "") or getattr(actor, "email", "")
            results.append({
                "id": str(item.id),
                "action": item.action,
                "status": item.status,
                "actor": {
                    "id": str(item.actor_id),
                    "name": actor_name,
                },
                "occurred_at": item.occurred_at,
                "model": item.model_used,
                "narrative": item.narrative_snapshot,
                "source_data": item.source_data_snapshot,
                "metadata": item.metadata,
            })
        return JsonResponse({"results": results})

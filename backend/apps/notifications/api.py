from django.http import JsonResponse
from django.utils import timezone
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.assessments.permissions import get_user_school
from .models import Notification


class NotificationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        school = get_user_school(request.user)
        qs = Notification.objects.filter(recipient=request.user)
        if school is not None:
            qs = qs.filter(school_id=school.id)
        unread_count = qs.filter(read_at__isnull=True).count()
        unread = request.query_params.get("unread") in {"1", "true", "True"}
        visible = qs.filter(read_at__isnull=True) if unread else qs
        results = [{
            "id": str(item.id), "title": item.title, "body": item.body,
            "type": item.notification_type, "link": item.link,
            "is_read": item.is_read, "created_at": item.created_at,
            "read_at": item.read_at,
        } for item in visible[:50]]
        return JsonResponse({"results": results, "unread_count": unread_count})


class NotificationReadView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        school = get_user_school(request.user)
        notification = Notification.objects.filter(id=notification_id, recipient=request.user).first()
        if notification is None:
            return JsonResponse({"detail": "Notification not found."}, status=404)
        if school is not None and notification.school_id != school.id:
            raise PermissionDenied("Notification does not belong to your institution.")
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at", "updated_at"])
        return JsonResponse({"id": str(notification.id), "is_read": True, "read_at": notification.read_at})


class NotificationMarkAllReadView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        school = get_user_school(request.user)
        qs = Notification.objects.filter(recipient=request.user, read_at__isnull=True)
        if school is not None:
            qs = qs.filter(school_id=school.id)
        count = qs.update(read_at=timezone.now())
        return JsonResponse({"marked_read": count})

from django.urls import path

from .api import NotificationMarkAllReadView, NotificationReadView, NotificationView

urlpatterns = [
    path("notifications/", NotificationView.as_view(), name="notifications"),
    path("notifications/mark-all-read/", NotificationMarkAllReadView.as_view(), name="notifications-mark-all-read"),
    path("notifications/<uuid:notification_id>/read/", NotificationReadView.as_view(), name="notification-read"),
]

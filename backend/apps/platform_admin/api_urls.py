from django.urls import path

from .api import (
    InstitutionOverviewView,
    PlatformAuditLogView,
    PlatformSettingsView,
    PlatformSummaryView,
    PlatformUserListView,
    PlatformUserStatusView,
    SchoolAdministratorCreateView,
)

urlpatterns = [
    path("platform/summary/", PlatformSummaryView.as_view(), name="platform-summary"),
    path("platform/users/", PlatformUserListView.as_view(), name="platform-users"),
    path("platform/users/<uuid:user_id>/status/", PlatformUserStatusView.as_view(), name="platform-user-status"),
    path("platform/audit-logs/", PlatformAuditLogView.as_view(), name="platform-audit-logs"),
    path("platform/settings/", PlatformSettingsView.as_view(), name="platform-settings"),
    path("platform/institutions/<uuid:school_id>/", InstitutionOverviewView.as_view(), name="platform-institution-overview"),
    path("platform/institutions/<uuid:school_id>/administrators/", SchoolAdministratorCreateView.as_view(), name="platform-school-administrator-create"),
]

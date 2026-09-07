"""URL configuration for the Key API."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.assessment_report_api import AssessmentResultsReportView
from apps.attendance_report_api import AttendanceReportView
from apps.class_report_api import ClassReportView
from apps.competency_report_api import CompetencyOutcomesReportView
from apps.report_api import StudentReportView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/", include("apps.identity.api_urls")),
    path("api/", include("apps.schools.api_urls")),
    path("api/", include("apps.students.api_urls")),
    path("api/", include("apps.teachers.api_urls")),
    path("api/", include("apps.academics.api_urls")),
    path("api/", include("apps.enrollment.api_urls")),
    path("api/", include("apps.lessons.api_urls")),
    path("api/", include("apps.attendance.api_urls")),
    path("api/", include("apps.assessments.api_urls")),
    path("api/", include("apps.portfolio.api_urls")),
    path("api/", include("apps.analytics_urls")),
    path("api/reports/student/", StudentReportView.as_view(), name="student-report"),
    path("api/reports/class/", ClassReportView.as_view(), name="class-report"),
    path("api/reports/attendance/", AttendanceReportView.as_view(), name="attendance-report"),
    path("api/reports/assessments/", AssessmentResultsReportView.as_view(), name="assessment-results-report"),
    path("api/reports/competencies/", CompetencyOutcomesReportView.as_view(), name="competency-outcomes-report"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

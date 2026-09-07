from django.urls import path

from .analytics_api import AnalyticsView

urlpatterns = [
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
]

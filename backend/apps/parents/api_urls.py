from django.urls import path

from .api import ParentManagementView

urlpatterns = [
    path("parents/", ParentManagementView.as_view(), name="parent-management"),
]

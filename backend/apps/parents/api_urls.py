from django.urls import path

from .api import ParentManagementView
from .self_api import ParentChildrenView

urlpatterns = [
    path("parents/", ParentManagementView.as_view(), name="parent-management"),
    path("parents/me/children/", ParentChildrenView.as_view(), name="parent-children"),
]

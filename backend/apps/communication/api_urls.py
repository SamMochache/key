from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CommunicationContactsView, CommunicationMessageViewSet

router = DefaultRouter()
router.register("messages", CommunicationMessageViewSet, basename="communication-message")

urlpatterns = router.urls + [
    path("communication/contacts/", CommunicationContactsView.as_view({"get": "list"}), name="communication-contacts"),
]

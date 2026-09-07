from rest_framework.routers import DefaultRouter

from .views import AttendanceRegisterViewSet

router = DefaultRouter()
router.register("attendance", AttendanceRegisterViewSet, basename="attendance-register")

urlpatterns = router.urls

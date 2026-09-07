from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, TeacherViewSet

router = DefaultRouter()
router.register("teachers", TeacherViewSet, basename="teacher")
router.register("departments", DepartmentViewSet, basename="department")

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, TeacherSubjectViewSet, TeacherViewSet

router = DefaultRouter()
router.register("teachers", TeacherViewSet, basename="teacher")
router.register("departments", DepartmentViewSet, basename="department")
router.register("teacher-subjects", TeacherSubjectViewSet, basename="teacher-subject")

urlpatterns = router.urls

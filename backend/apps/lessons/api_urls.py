from rest_framework.routers import DefaultRouter

from .views import LessonSessionViewSet

router = DefaultRouter()
router.register("lessons", LessonSessionViewSet, basename="lesson")
urlpatterns = router.urls

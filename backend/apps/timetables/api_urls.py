from rest_framework.routers import DefaultRouter

from .views import PeriodViewSet, TimetableEntryViewSet, TimetableViewSet

router = DefaultRouter()
router.register("periods", PeriodViewSet, basename="period")
router.register("timetables", TimetableViewSet, basename="timetable")
router.register("timetable-entries", TimetableEntryViewSet, basename="timetable-entry")

urlpatterns = router.urls

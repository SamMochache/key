from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet,
    CambridgeStageViewSet,
    ClassroomViewSet,
    CurriculumViewSet,
    MontessoriLevelViewSet,
    StageSubjectViewSet,
    SubjectViewSet,
    TermViewSet,
)

router = DefaultRouter()
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("terms", TermViewSet, basename="term")
router.register("curricula", CurriculumViewSet, basename="curriculum")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("cambridge-stages", CambridgeStageViewSet, basename="cambridge-stage")
router.register("montessori-levels", MontessoriLevelViewSet, basename="montessori-level")
router.register("stage-subjects", StageSubjectViewSet, basename="stage-subject")
router.register("classrooms", ClassroomViewSet, basename="classroom")

urlpatterns = router.urls

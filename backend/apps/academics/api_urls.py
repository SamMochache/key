from django.urls import path
from rest_framework.routers import DefaultRouter

from .admin_actions import SetCurrentAcademicYearView, SetCurrentTermView
from .views import (
    AcademicYearViewSet,
    CambridgeStageViewSet,
    ClassroomViewSet,
    CurriculumViewSet,
    MontessoriLevelViewSet,
    ProgrammeViewSet,
    StageSubjectViewSet,
    SubjectViewSet,
    TermViewSet,
)

router = DefaultRouter()
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("terms", TermViewSet, basename="term")
router.register("curricula", CurriculumViewSet, basename="curriculum")
router.register("programmes", ProgrammeViewSet, basename="programme")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("cambridge-stages", CambridgeStageViewSet, basename="cambridge-stage")
router.register("montessori-levels", MontessoriLevelViewSet, basename="montessori-level")
router.register("stage-subjects", StageSubjectViewSet, basename="stage-subject")
router.register("classrooms", ClassroomViewSet, basename="classroom")

urlpatterns = [
    path("academic-years/<uuid:pk>/set-current/", SetCurrentAcademicYearView.as_view(), name="academic-year-set-current"),
    path("terms/<uuid:pk>/set-current/", SetCurrentTermView.as_view(), name="term-set-current"),
] + router.urls

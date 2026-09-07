from rest_framework.routers import DefaultRouter

from .api_views import (
    AssessmentEvaluationViewSet,
    AssessmentSubmissionViewSet,
    AssessmentViewSet,
    CompetencyEvaluationViewSet,
    CriterionScoreViewSet,
    DashboardSummaryView,
    RubricCriterionViewSet,
    RubricViewSet,
)
from .competency_api_views import CompetencyViewSet
from .evidence_api_views import EvidenceViewSet

router = DefaultRouter()
router.register("assessments", AssessmentViewSet, basename="assessment")
router.register("submissions", AssessmentSubmissionViewSet, basename="assessment-submission")
router.register("rubrics", RubricViewSet, basename="rubric")
router.register("rubric-criteria", RubricCriterionViewSet, basename="rubric-criterion")
router.register("evaluations", AssessmentEvaluationViewSet, basename="assessment-evaluation")
router.register("criterion-scores", CriterionScoreViewSet, basename="criterion-score")
router.register("competency-evaluations", CompetencyEvaluationViewSet, basename="competency-evaluation")
router.register("dashboard-summary", DashboardSummaryView, basename="dashboard-summary")
router.register("competencies", CompetencyViewSet, basename="competency")
router.register("evidence", EvidenceViewSet, basename="evidence")

urlpatterns = router.urls

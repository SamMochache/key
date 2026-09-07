from rest_framework.routers import DefaultRouter

from .api_views import ArtifactViewSet, PortfolioItemViewSet, PortfolioViewSet

router = DefaultRouter()
router.register("portfolios", PortfolioViewSet, basename="portfolio")
router.register("portfolio-items", PortfolioItemViewSet, basename="portfolio-item")
router.register("portfolio-artifacts", ArtifactViewSet, basename="portfolio-artifact")

urlpatterns = router.urls

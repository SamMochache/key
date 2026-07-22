from apps.ai_reports.dto import PortfolioContext
from apps.portfolio.models import PortfolioItem


class PortfolioSelectors:
    """
    Read-only portfolio queries.
    """

    def build_context(
        self,
        enrollment,
    ) -> list[PortfolioContext]:

        queryset = PortfolioItem.objects.filter(
            enrollment=enrollment,
        )

        return [
            PortfolioContext(
                title=item.title,
                item_type=item.item_type,
                description=item.description,
                event_date=item.event_date,
            )
            for item in queryset
        ]
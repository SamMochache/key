from apps.ai_reports.dto import CompetencyContext
from apps.assessments.models import CompetencyAssessment


class CompetencySelectors:
    """
    Read-only competency queries.
    """

    def build_context(
        self,
        enrollment,
    ) -> list[CompetencyContext]:

        queryset = (
            CompetencyAssessment.objects.filter(
                enrollment=enrollment,
            )
            .select_related(
                "competency",
            )
        )

        return [
            CompetencyContext(
                competency=item.competency.name,
                level=item.level,
                teacher_comment=item.teacher_comment,
            )
            for item in queryset
        ]
    
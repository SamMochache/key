from apps.ai_reports.dto import ObservationContext
from apps.teachers.models import TeacherObservation


class ObservationSelectors:
    """
    Read-only teacher observation queries.
    """

    def build_context(
        self,
        enrollment,
    ) -> list[ObservationContext]:

        queryset = TeacherObservation.objects.filter(
            enrollment=enrollment,
        )

        return [
            ObservationContext(
                observation_date=item.observation_date,
                title=item.title,
                observation=item.observation,
            )
            for item in queryset
        ]
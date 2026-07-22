from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ObservationContext:
    """
    Teacher observation used by AI reports.
    """

    observation_date: date

    title: str

    observation: str
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class PortfolioContext:
    """
    Portfolio evidence available for AI reports.
    """

    title: str

    item_type: str

    description: str

    event_date: date
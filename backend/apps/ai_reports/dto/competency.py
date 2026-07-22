from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompetencyContext:
    """
    Competency evaluation used by AI reports.
    """

    competency: str

    level: str

    teacher_comment: str
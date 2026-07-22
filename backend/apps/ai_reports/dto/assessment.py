from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AssessmentContext:
    """
    Assessment summary used by AI reports.
    """

    assessment: str

    subject: str

    score: float

    maximum_score: float

    percentage: float

    teacher_feedback: str
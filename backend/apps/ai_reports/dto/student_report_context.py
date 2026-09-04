from dataclasses import dataclass, field

from .assessment import AssessmentContext
from .attendance import AttendanceContext
from .competency import CompetencyContext
from .observation import ObservationContext
from .portfolio import PortfolioContext


@dataclass(frozen=True, slots=True)
class StudentReportContext:
    """
    Complete learner context supplied to the AI pipeline.
    """

    student_id: str

    admission_number: str

    student_name: str

    classroom: str

    academic_year: str

    term: str

    attendance: AttendanceContext

    assessments: list[AssessmentContext] = field(default_factory=list)

    competencies: list[CompetencyContext] = field(default_factory=list)

    portfolio: list[PortfolioContext] = field(default_factory=list)

    observations: list[ObservationContext] = field(default_factory=list)
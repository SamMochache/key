from apps.ai_reports.dto import StudentReportContext


class StudentContextBuilder:
    """
    Builds the complete context supplied to the AI report generator.

    This class orchestrates multiple selectors and converts the
    retrieved data into a single immutable StudentReportContext.
    """

    def build(self, enrollment):
        raise NotImplementedError
from apps.assessments.models import AINarrativeReportHistory


def record_ai_report_history(report, action, actor, metadata=None, narrative=None):
    return AINarrativeReportHistory.objects.create(
        report=report,
        action=action,
        actor=actor,
        status=report.status,
        model_used=report.model_used,
        narrative_snapshot=narrative if narrative is not None else (report.edited_content or report.generated_content),
        source_data_snapshot=report.source_data_snapshot,
        metadata=metadata or {},
    )

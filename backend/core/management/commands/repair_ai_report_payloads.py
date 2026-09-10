from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.assessments.models import AINarrativeReport
from apps.enrollment.models import Enrollment


class Command(BaseCommand):
    help = "Normalize legacy AI narrative report payloads to the current student/parent UI contract."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist the normalized payloads. Without this flag the command only reports what would change.",
        )

    def _normalize_narrative(self, report):
        content = report.edited_content or report.generated_content or {}
        if not isinstance(content, dict):
            return {}, True

        normalized = {
            "summary": content.get("summary", content.get("overall_progress", "")),
            "strengths": content.get("strengths", ""),
            "development_areas": content.get("development_areas", ""),
            "next_steps": content.get("next_steps", content.get("suggested_next_steps", "")),
            "teacher_note": content.get("teacher_note", content.get("teacher_review_note", "")),
        }
        changed = normalized != content
        return normalized, changed

    def _normalize_facts(self, report):
        facts = report.source_data_snapshot or {}
        if not isinstance(facts, dict):
            facts = {}

        # Current payloads already satisfy the contract.
        required = {"learner", "period", "assessment", "attendance", "competencies", "portfolio"}
        if required.issubset(facts):
            return facts, False

        enrollment = Enrollment.objects.select_related(
            "classroom", "classroom__cambridge_stage", "academic_year", "term"
        ).filter(
            student_id=report.student_id,
            academic_year_id=report.academic_year_id,
            term_id=report.term_id,
        ).first()

        learner = facts.get("learner") if isinstance(facts.get("learner"), dict) else {}
        first_name = learner.get("first_name") or getattr(report.student.user, "first_name", "Learner") or "Learner"
        admission_number = learner.get("admission_number") or report.student.admission_number
        classroom_name = learner.get("class")
        stage_name = learner.get("stage")
        if enrollment is not None:
            classroom_name = classroom_name or enrollment.classroom.name
            stage_name = stage_name or (
                enrollment.classroom.cambridge_stage.name
                if enrollment.classroom.cambridge_stage_id
                else None
            )

        normalized = {
            "learner": {
                "first_name": first_name,
                "admission_number": admission_number,
                "class": classroom_name or "Not recorded",
                "stage": stage_name,
            },
            "period": {
                "academic_year": facts.get("academic_year")
                or (enrollment.academic_year.name if enrollment is not None else report.academic_year.name),
                "term": facts.get("term_number")
                or (enrollment.term.term_number if enrollment is not None else report.term.term_number),
            },
            "assessment": facts.get("assessment") if isinstance(facts.get("assessment"), dict) else {
                "published_results": 0,
                "average_percentage": None,
            },
            "attendance": facts.get("attendance") if isinstance(facts.get("attendance"), dict) else {
                "recorded_sessions": 0,
                "attendance_percentage": None,
            },
            "competencies": facts.get("competencies") if isinstance(facts.get("competencies"), list) else [],
            "portfolio": facts.get("portfolio") if isinstance(facts.get("portfolio"), dict) else {
                "items": 0,
                "artifacts": 0,
            },
        }
        return normalized, normalized != facts

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        reports = AINarrativeReport.objects.select_related("student__user", "academic_year", "term")
        changed_count = 0

        for report in reports.iterator():
            narrative, narrative_changed = self._normalize_narrative(report)
            facts, facts_changed = self._normalize_facts(report)
            if not narrative_changed and not facts_changed:
                continue

            changed_count += 1
            action = "would repair" if not apply_changes else "repairing"
            self.stdout.write(f"{action} {report.id} — {report.student.user.full_name}")

            if apply_changes:
                report.generated_content = narrative if narrative_changed else report.generated_content
                report.edited_content = narrative if narrative_changed else report.edited_content
                report.source_data_snapshot = facts
                report.save(update_fields=["generated_content", "edited_content", "source_data_snapshot", "updated_at"])

        if apply_changes:
            self.stdout.write(self.style.SUCCESS(f"Repaired {changed_count} AI report payload(s)."))
        else:
            self.stdout.write(self.style.WARNING(
                f"Found {changed_count} AI report payload(s) requiring repair. Run with --apply to persist changes."
            ))

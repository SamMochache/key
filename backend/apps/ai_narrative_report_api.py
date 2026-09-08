import json
import os
from collections import defaultdict
from urllib import error, request

from django.http import JsonResponse
from django.utils import timezone
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.academics.models import AcademicYear, Term
from apps.ai_narrative_report_audit import record_ai_report_history
from apps.assessments.models import (
    AINarrativeReport,
    AINarrativeReportHistory,
    AssessmentSubmission,
    CompetencyEvaluation,
)
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.portfolio.models import PortfolioItem
from core.constants.enrollment import EnrollmentStatus


LEVEL_ORDER = {"BEGINNING": 1, "DEVELOPING": 2, "PROFICIENT": 3, "ADVANCED": 4}
LEVEL_LABELS = {
    "BEGINNING": "Beginning",
    "DEVELOPING": "Developing",
    "PROFICIENT": "Proficient",
    "ADVANCED": "Advanced",
}
REPORTABLE_ENROLLMENT_STATUSES = [
    EnrollmentStatus.ENROLLED,
    EnrollmentStatus.PROMOTED,
    EnrollmentStatus.TRANSFERRED,
    EnrollmentStatus.WITHDRAWN,
    EnrollmentStatus.GRADUATED,
]


class AIRuntimeError(Exception):
    pass


def _provider_settings():
    provider = os.getenv("AI_REPORT_PROVIDER", "gemini").lower()
    if provider == "openai":
        return provider, os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_AI_REPORT_MODEL", "gpt-5.6-luna")
    return provider, os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_AI_REPORT_MODEL", "gemini-3-flash-preview")


def _extract_gemini_text(payload):
    parts = []
    for candidate in payload.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            value = part.get("text")
            if isinstance(value, str):
                parts.append(value)
    return "".join(parts).strip()


def _extract_openai_text(payload):
    text = payload.get("output_text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    parts = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            value = content.get("text")
            if isinstance(value, str):
                parts.append(value)
    return "".join(parts).strip()


def _parse_narrative(output):
    if not output:
        raise AIRuntimeError("The AI provider returned an empty narrative.")
    try:
        result = json.loads(output)
    except json.JSONDecodeError as exc:
        raise AIRuntimeError("The AI provider returned an invalid narrative format.") from exc

    required = {"summary", "strengths", "development_areas", "next_steps", "teacher_note"}
    if not required.issubset(result):
        raise AIRuntimeError("The AI provider returned an incomplete narrative.")
    return {key: str(result[key]).strip() for key in required}


def _generate_narrative(facts):
    provider, api_key, model = _provider_settings()
    if not api_key:
        variable = "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY"
        raise AIRuntimeError(f"{variable} is not configured on the backend.")

    instructions = """
You are the narrative-reporting assistant for a school management system.
Generate a professional learner progress narrative from ONLY the supplied facts.
Never invent scores, attendance, competencies, activities, behaviour, causes, or
personal details. If a fact is missing, do not speculate. Do not diagnose a learner.
Use warm, specific, growth-focused language suitable for a teacher-reviewed school
report. Avoid exaggerated praise and avoid making high-stakes recommendations.

Return valid JSON with exactly these string fields:
summary, strengths, development_areas, next_steps, teacher_note.
Each field should be a concise paragraph. Refer to the learner by first name only.
""".strip()
    user_input = json.dumps(facts, ensure_ascii=False)

    if provider == "openai":
        body = json.dumps({
            "model": model,
            "instructions": instructions,
            "input": user_input,
            "max_output_tokens": 900,
        }).encode("utf-8")
        endpoint = "https://api.openai.com/v1/responses"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    else:
        schema = {
            "type": "OBJECT",
            "properties": {
                "summary": {"type": "STRING"},
                "strengths": {"type": "STRING"},
                "development_areas": {"type": "STRING"},
                "next_steps": {"type": "STRING"},
                "teacher_note": {"type": "STRING"},
            },
            "required": ["summary", "strengths", "development_areas", "next_steps", "teacher_note"],
        }
        body = json.dumps({
            "systemInstruction": {"parts": [{"text": instructions}]},
            "contents": [{"role": "user", "parts": [{"text": user_input}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": schema,
                "maxOutputTokens": 900,
            },
        }).encode("utf-8")
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        }

    req = request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AIRuntimeError(f"AI provider returned HTTP {exc.code}: {detail[:500]}") from exc
    except error.URLError as exc:
        raise AIRuntimeError("Unable to reach the AI provider.") from exc

    output = _extract_openai_text(payload) if provider == "openai" else _extract_gemini_text(payload)
    return _parse_narrative(output)


def _build_facts(enrollment, year, term):
    submissions = AssessmentSubmission.objects.filter(
        enrollment=enrollment,
        evaluation__published=True,
        assessment__status="PUBLISHED",
    ).select_related("assessment", "evaluation")
    scores = list(submissions.values_list("evaluation__percentage", flat=True))
    assessment_average = float(sum(scores) / len(scores)) if scores else None

    attendance_records = AttendanceRecord.objects.filter(enrollment=enrollment)
    attendance_total = attendance_records.count()
    attendance_attended = attendance_records.filter(status__in=["PRESENT", "LATE"]).count()
    attendance_rate = round(attendance_attended * 100 / attendance_total, 1) if attendance_total else None

    competency_values = defaultdict(list)
    for item in CompetencyEvaluation.objects.filter(
        evaluation__submission__enrollment=enrollment,
        evaluation__published=True,
    ).select_related("competency"):
        competency_values[item.competency.name].append(item.level)

    competencies = []
    for name, levels in competency_values.items():
        numeric = [LEVEL_ORDER[level] for level in levels if level in LEVEL_ORDER]
        average = round(sum(numeric) / len(numeric), 2) if numeric else None
        strongest = max(levels, key=lambda level: LEVEL_ORDER.get(level, 0)) if levels else None
        competencies.append({
            "name": name,
            "observations": len(levels),
            "highest_level": LEVEL_LABELS.get(strongest, "Not recorded"),
            "average_level": average,
        })
    competencies.sort(key=lambda item: item["name"].lower())

    portfolio_items = PortfolioItem.objects.filter(
        portfolio__student=enrollment.student,
        event_date__gte=year.start_date,
        event_date__lte=year.end_date,
    ).prefetch_related("artifacts")
    portfolio_count = portfolio_items.count()
    artifact_count = sum(item.artifacts.count() for item in portfolio_items)

    first_name = enrollment.student.user.first_name if hasattr(enrollment.student, "user") else "Learner"
    return {
        "learner": {
            "first_name": first_name or "Learner",
            "admission_number": enrollment.student.admission_number,
            "class": enrollment.classroom.name,
            "stage": enrollment.classroom.cambridge_stage.name if enrollment.classroom.cambridge_stage else None,
        },
        "period": {"academic_year": year.name, "term": term.term_number},
        "assessment": {
            "published_results": len(scores),
            "average_percentage": round(assessment_average, 1) if assessment_average is not None else None,
        },
        "attendance": {
            "recorded_sessions": attendance_total,
            "attendance_percentage": attendance_rate,
        },
        "competencies": competencies,
        "portfolio": {"items": portfolio_count, "artifacts": artifact_count},
    }


def _report_payload(report):
    content = report.edited_content or report.generated_content
    return {
        "id": str(report.id),
        "status": report.status,
        "student": str(report.student_id),
        "academic_year": str(report.academic_year_id),
        "term": str(report.term_id),
        "facts": report.source_data_snapshot,
        "narrative": content,
        "generated_content": report.generated_content,
        "edited_content": report.edited_content,
        "review_required": report.status != AINarrativeReport.Status.PUBLISHED,
        "model": report.model_used,
        "generated_at": report.generated_at,
        "reviewed_at": report.reviewed_at,
        "published_at": report.published_at,
    }


def _staff_school(request):
    role = get_user_role(request.user)
    if role not in {UserRole.ADMIN, UserRole.TEACHER}:
        raise PermissionDenied("Only staff can manage AI narrative reports.")
    return role, get_user_school(request.user)


def _get_report_for_staff(request, report_id):
    _, school = _staff_school(request)
    report = AINarrativeReport.objects.select_related(
        "student", "academic_year", "term", "generated_by", "reviewed_by", "published_by"
    ).filter(id=report_id).first()
    if report is None:
        return None
    if school is not None and not Enrollment.objects.filter(
        student_id=report.student_id,
        academic_year_id=report.academic_year_id,
        term_id=report.term_id,
        classroom__school_id=school.id,
    ).exists():
        raise PermissionDenied("The report does not belong to your institution.")
    return report


class AINarrativeReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        _, school = _staff_school(request)
        reports = AINarrativeReport.objects.select_related("student", "academic_year", "term")
        if school is not None:
            reports = reports.filter(student__enrollments__classroom__school_id=school.id).distinct()
        if request.query_params.get("student"):
            reports = reports.filter(student_id=request.query_params["student"])
        if request.query_params.get("academic_year"):
            reports = reports.filter(academic_year_id=request.query_params["academic_year"])
        if request.query_params.get("term"):
            reports = reports.filter(term_id=request.query_params["term"])
        return JsonResponse({"results": [_report_payload(report) for report in reports[:50]]})

    def post(self, request):
        _, school = _staff_school(request)
        student_id = request.data.get("student")
        year_id = request.data.get("academic_year")
        term_id = request.data.get("term")
        if not student_id or not year_id or not term_id:
            return JsonResponse({"detail": "Student, academic year, and term are required."}, status=400)

        year = AcademicYear.objects.filter(id=year_id).first()
        term = Term.objects.select_related("academic_year").filter(id=term_id, academic_year_id=year_id).first()
        if year is None or term is None:
            return JsonResponse({"detail": "The selected academic year or term was not found."}, status=404)

        enrollment = Enrollment.objects.select_related(
            "student", "student__user", "classroom", "classroom__school", "classroom__cambridge_stage"
        ).filter(
            student_id=student_id,
            academic_year_id=year.id,
            term_id=term.id,
            status__in=REPORTABLE_ENROLLMENT_STATUSES,
        ).first()
        if enrollment is None:
            return JsonResponse({"detail": "The student is not enrolled in the selected academic period."}, status=404)
        if school is not None and enrollment.classroom.school_id != school.id:
            raise PermissionDenied("The student does not belong to your institution.")

        existing = AINarrativeReport.objects.filter(student_id=student_id, academic_year_id=year.id, term_id=term.id).first()
        if existing and existing.status == AINarrativeReport.Status.PUBLISHED:
            return JsonResponse({"detail": "A published report already exists for this learner and period."}, status=409)

        facts = _build_facts(enrollment, year, term)
        try:
            narrative = _generate_narrative(facts)
        except AIRuntimeError as exc:
            return JsonResponse({"detail": str(exc)}, status=503)

        _, _, model = _provider_settings()
        report, created = AINarrativeReport.objects.update_or_create(
            student_id=student_id,
            academic_year_id=year.id,
            term_id=term.id,
            defaults={
                "generated_content": narrative,
                "edited_content": {},
                "source_data_snapshot": facts,
                "status": AINarrativeReport.Status.DRAFT,
                "generated_by": request.user,
                "reviewed_by": None,
                "published_by": None,
                "model_used": model,
                "reviewed_at": None,
                "published_at": None,
            },
        )
        record_ai_report_history(
            report,
            AINarrativeReportHistory.Action.GENERATED,
            request.user,
            metadata={"regenerated": not created},
        )
        return JsonResponse(_report_payload(report), status=201)

    def patch(self, request):
        report_id = request.data.get("id")
        if not report_id:
            return JsonResponse({"detail": "Report id is required."}, status=400)
        report = _get_report_for_staff(request, report_id)
        if report is None:
            return JsonResponse({"detail": "Report not found."}, status=404)
        if report.status == AINarrativeReport.Status.PUBLISHED:
            return JsonResponse({"detail": "Published reports are read-only."}, status=409)

        edited_content = request.data.get("narrative")
        if not isinstance(edited_content, dict):
            return JsonResponse({"detail": "narrative must be an object."}, status=400)
        required = {"summary", "strengths", "development_areas", "next_steps", "teacher_note"}
        if set(edited_content) != required:
            return JsonResponse({"detail": "narrative must contain the five report sections."}, status=400)
        if any(not isinstance(value, str) or not value.strip() for value in edited_content.values()):
            return JsonResponse({"detail": "All narrative sections must contain text."}, status=400)

        previous_narrative = report.edited_content or report.generated_content
        report.edited_content = {key: value.strip() for key, value in edited_content.items()}
        report.status = AINarrativeReport.Status.REVIEWED
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save(update_fields=["edited_content", "status", "reviewed_by", "reviewed_at", "updated_at"])
        record_ai_report_history(
            report,
            AINarrativeReportHistory.Action.EDITED,
            request.user,
            metadata={"previous_narrative": previous_narrative},
        )
        record_ai_report_history(
            report,
            AINarrativeReportHistory.Action.REVIEWED,
            request.user,
        )
        return JsonResponse(_report_payload(report))


class AINarrativeReportPublishView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, report_id):
        report = _get_report_for_staff(request, report_id)
        if report is None:
            return JsonResponse({"detail": "Report not found."}, status=404)
        if report.status != AINarrativeReport.Status.REVIEWED:
            return JsonResponse({"detail": "A report must be reviewed before publication."}, status=409)
        if not report.edited_content:
            return JsonResponse({"detail": "A reviewed report must contain edited content."}, status=409)

        report.status = AINarrativeReport.Status.PUBLISHED
        report.published_by = request.user
        report.published_at = timezone.now()
        report.save(update_fields=["status", "published_by", "published_at", "updated_at"])
        record_ai_report_history(
            report,
            AINarrativeReportHistory.Action.PUBLISHED,
            request.user,
        )
        return JsonResponse(_report_payload(report))

import json
import os
from collections import defaultdict
from urllib import error, request

from django.db.models import Avg
from django.http import JsonResponse
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.academics.models import AcademicYear, Classroom, Term
from apps.assessments.models import AssessmentSubmission, CompetencyEvaluation
from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.attendance.models import AttendanceRecord
from apps.enrollment.models import Enrollment
from apps.portfolio.models import PortfolioItem


LEVEL_ORDER = {"BEGINNING": 1, "DEVELOPING": 2, "PROFICIENT": 3, "ADVANCED": 4}
LEVEL_LABELS = {
    "BEGINNING": "Beginning",
    "DEVELOPING": "Developing",
    "PROFICIENT": "Proficient",
    "ADVANCED": "Advanced",
}


class AIRuntimeError(Exception):
    pass


def _extract_output_text(payload):
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


def _generate_narrative(facts):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIRuntimeError("OPENAI_API_KEY is not configured on the backend.")

    model = os.getenv("OPENAI_AI_REPORT_MODEL", "gpt-5.6-luna")
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
    body = json.dumps({
        "model": model,
        "instructions": instructions,
        "input": user_input,
        "max_output_tokens": 900,
    }).encode("utf-8")

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AIRuntimeError(f"AI provider returned HTTP {exc.code}: {detail[:500]}") from exc
    except error.URLError as exc:
        raise AIRuntimeError("Unable to reach the AI provider.") from exc

    output = _extract_output_text(payload)
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


class AINarrativeReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role = get_user_role(request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can generate AI narrative reports.")

        school = get_user_school(request.user)
        if school is None and role != UserRole.ADMIN:
            raise PermissionDenied("Your account is not associated with an institution.")

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
            "student", "classroom", "classroom__school", "classroom__cambridge_stage"
        ).filter(
            student_id=student_id,
            academic_year_id=year.id,
            term_id=term.id,
            status__in=["ACTIVE", "COMPLETED"],
        ).first()
        if enrollment is None:
            return JsonResponse({"detail": "The student is not enrolled in the selected academic period."}, status=404)
        if school is not None and enrollment.classroom.school_id != school.id:
            raise PermissionDenied("The student does not belong to your institution.")

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
        facts = {
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

        try:
            narrative = _generate_narrative(facts)
        except AIRuntimeError as exc:
            return JsonResponse({"detail": str(exc)}, status=503)

        return JsonResponse({
            "status": "generated",
            "facts": facts,
            "narrative": narrative,
            "review_required": True,
            "model": os.getenv("OPENAI_AI_REPORT_MODEL", "gpt-5.6-luna"),
        })

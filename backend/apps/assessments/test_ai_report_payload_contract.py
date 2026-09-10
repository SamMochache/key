from datetime import date

from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, Term
from apps.assessments.models import AINarrativeReport
from apps.enrollment.models import Enrollment
from apps.identity.models import User
from apps.schools.models import School
from apps.students.models import Student
from core.constants.enrollment import EnrollmentStatus


class AIReportPayloadContractTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name="Contract Test School", short_name="AI-CONTRACT", city="Nairobi")
        self.year = AcademicYear.objects.create(
            school=self.school,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
        )
        self.term = Term.objects.create(
            academic_year=self.year,
            term_number=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            is_current=True,
        )
        curriculum = Curriculum.objects.create(name="Contract Curriculum", version="1.0")
        programme = Programme.objects.create(curriculum=curriculum, name="Cambridge Primary")
        stage = CambridgeStage.objects.create(programme=programme, name="Stage 3", stage_number=3, display_order=3)
        self.classroom = Classroom.objects.create(
            school=self.school,
            academic_year=self.year,
            term=self.term,
            cambridge_stage=stage,
            name="Ocean",
            code="OCEAN",
            capacity=25,
        )
        self.user = User.objects.create_user(
            email="contract.student@test.example",
            password="StrongPassword123!",
            first_name="Contract",
            last_name="Student",
        )
        self.student = Student.objects.create(
            user=self.user,
            school=self.school,
            admission_number="AI-CONTRACT-001",
            admission_date=date(2026, 1, 1),
            date_of_birth=date(2018, 1, 1),
            gender="male",
        )
        Enrollment.objects.create(
            student=self.student,
            academic_year=self.year,
            term=self.term,
            classroom=self.classroom,
            enrollment_date=self.term.start_date,
            status=EnrollmentStatus.ENROLLED,
        )
        self.admin = User.objects.create_superuser(
            email="contract.admin@test.example",
            password="StrongPassword123!",
        )

    def test_published_endpoint_returns_canonical_shape_for_legacy_payload(self):
        narrative = {
            "overall_progress": "Good progress.",
            "strengths": "Strong participation.",
            "development_areas": "Keep practising.",
            "suggested_next_steps": "Build more evidence.",
            "teacher_review_note": "Reviewed.",
        }
        AINarrativeReport.objects.create(
            student=self.student,
            academic_year=self.year,
            term=self.term,
            generated_content=narrative,
            edited_content=narrative,
            source_data_snapshot={
                "student_id": str(self.student.id),
                "student_name": self.student.user.full_name,
                "academic_year": self.year.name,
                "term_number": self.term.term_number,
            },
            status=AINarrativeReport.Status.PUBLISHED,
            generated_by=self.admin,
            reviewed_by=self.admin,
            published_by=self.admin,
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("published-ai-narrative-reports"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["results"], [])

    def test_repair_command_normalizes_legacy_payload(self):
        narrative = {
            "overall_progress": "Good progress.",
            "strengths": "Strong participation.",
            "development_areas": "Keep practising.",
            "suggested_next_steps": "Build more evidence.",
            "teacher_review_note": "Reviewed.",
        }
        report = AINarrativeReport.objects.create(
            student=self.student,
            academic_year=self.year,
            term=self.term,
            generated_content=narrative,
            edited_content=narrative,
            source_data_snapshot={
                "student_id": str(self.student.id),
                "student_name": self.student.user.full_name,
                "academic_year": self.year.name,
                "term_number": self.term.term_number,
            },
            status=AINarrativeReport.Status.PUBLISHED,
            generated_by=self.admin,
            reviewed_by=self.admin,
            published_by=self.admin,
        )

        call_command("repair_ai_report_payloads", "--apply")
        report.refresh_from_db()

        self.assertEqual(report.edited_content["summary"], "Good progress.")
        self.assertEqual(report.edited_content["next_steps"], "Build more evidence.")
        self.assertEqual(report.edited_content["teacher_note"], "Reviewed.")
        self.assertIn("learner", report.source_data_snapshot)
        self.assertIn("assessment", report.source_data_snapshot)
        self.assertIn("attendance", report.source_data_snapshot)
        self.assertIn("portfolio", report.source_data_snapshot)

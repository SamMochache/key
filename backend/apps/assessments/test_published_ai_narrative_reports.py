from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, Term
from apps.assessments.models import AINarrativeReport
from apps.identity.models import User
from apps.parents.models import Parent, ParentStudentRelationship
from apps.schools.models import School
from apps.students.models import Student


class PublishedAINarrativeReportApiTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="AI Report Test School",
            short_name="AI-TEST",
            city="Nairobi",
        )
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
        curriculum = Curriculum.objects.create(name="Cambridge Primary", version="1.0")
        programme = Programme.objects.create(curriculum=curriculum, name="Cambridge Primary")
        stage = CambridgeStage.objects.create(
            programme=programme,
            name="Stage 3",
            stage_number=3,
            display_order=3,
        )
        self.classroom = Classroom.objects.create(
            school=self.school,
            academic_year=self.year,
            term=self.term,
            cambridge_stage=stage,
            name="Ocean",
            code="OCEAN",
            capacity=25,
        )

        self.student_user = User.objects.create_user(
            email="student@test.example",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Student",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            school=self.school,
            admission_number="AI-001",
            admission_date=date(2026, 1, 1),
            date_of_birth=date(2018, 1, 1),
            gender="male",
        )

        self.other_student_user = User.objects.create_user(
            email="other.student@test.example",
            password="StrongPassword123!",
            first_name="Other",
            last_name="Student",
        )
        self.other_student = Student.objects.create(
            user=self.other_student_user,
            school=self.school,
            admission_number="AI-002",
            admission_date=date(2026, 1, 1),
            date_of_birth=date(2018, 1, 1),
            gender="female",
        )

        self.admin = User.objects.create_superuser(
            email="admin@test.example",
            password="StrongPassword123!",
        )
        self.parent_user = User.objects.create_user(
            email="parent@test.example",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Parent",
        )
        self.parent = Parent.objects.create(user=self.parent_user, school=self.school)
        ParentStudentRelationship.objects.create(
            parent=self.parent,
            student=self.student,
            can_view_reports=True,
            is_active=True,
        )

        narrative = {
            "summary": "Test summary.",
            "strengths": "Test strengths.",
            "development_areas": "Test development areas.",
            "next_steps": "Test next steps.",
            "teacher_note": "Test teacher note.",
        }
        self.report = AINarrativeReport.objects.create(
            student=self.student,
            academic_year=self.year,
            term=self.term,
            generated_content=narrative,
            edited_content=narrative,
            source_data_snapshot={
                "learner": {
                    "first_name": "Test",
                    "admission_number": "AI-001",
                    "class": "Ocean",
                    "stage": "Stage 3",
                },
                "assessment": {"published_results": 1, "average_percentage": 90.0},
                "attendance": {"recorded_sessions": 1, "attendance_percentage": 100.0},
                "competencies": [],
                "portfolio": {"items": 0, "artifacts": 0},
            },
            status=AINarrativeReport.Status.PUBLISHED,
            generated_by=self.admin,
            reviewed_by=self.admin,
            published_by=self.admin,
        )

    def test_student_sees_own_published_report(self):
        self.client.force_authenticate(self.student_user)

        response = self.client.get(reverse("published-ai-narrative-reports"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["id"], str(self.report.id))
        self.assertEqual(response.json()["results"][0]["student"], str(self.student.id))

    def test_student_does_not_see_another_students_report(self):
        other_report = AINarrativeReport.objects.create(
            student=self.other_student,
            academic_year=self.year,
            term=self.term,
            generated_content=self.report.generated_content,
            edited_content=self.report.edited_content,
            source_data_snapshot=self.report.source_data_snapshot,
            status=AINarrativeReport.Status.PUBLISHED,
            generated_by=self.admin,
            reviewed_by=self.admin,
            published_by=self.admin,
        )
        self.client.force_authenticate(self.student_user)

        response = self.client.get(reverse("published-ai-narrative-reports"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.json()["results"]}
        self.assertIn(str(self.report.id), ids)
        self.assertNotIn(str(other_report.id), ids)

    def test_parent_sees_authorized_published_report(self):
        self.client.force_authenticate(self.parent_user)

        response = self.client.get(
            reverse("published-ai-narrative-reports"),
            {"student": str(self.student.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.json()["results"]], [str(self.report.id)])

    def test_parent_cannot_use_student_filter_to_bypass_relationship(self):
        self.client.force_authenticate(self.parent_user)

        response = self.client.get(
            reverse("published-ai-narrative-reports"),
            {"student": str(self.other_student.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["results"], [])

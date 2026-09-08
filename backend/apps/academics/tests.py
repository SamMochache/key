from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.identity.models import User
from apps.schools.models import School
from apps.enrollment.models import Enrollment

from .models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, StageSubject, Subject, Term


class AcademicsApiTests(APITestCase):
    def setUp(self):
        self.school_a = School.objects.create(name="School A", short_name="A", city="Nairobi")
        self.school_b = School.objects.create(name="School B", short_name="B", city="Nairobi")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="StrongPassword123!")

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Student",
        )
        from apps.students.models import Student

        self.student = Student.objects.create(
            user=self.student_user,
            school=self.school_a,
            admission_number="A-001",
            admission_date=date(2026, 1, 1),
            date_of_birth=date(2018, 1, 1),
            gender="male",
        )

        curriculum = Curriculum.objects.create(name="Cambridge Primary", version="1.0")
        programme = Programme.objects.create(curriculum=curriculum, name="Cambridge Primary")
        self.stage = CambridgeStage.objects.create(
            programme=programme,
            name="Stage 3",
            stage_number=3,
            display_order=3,
        )
        self.subject = Subject.objects.create(
            curriculum=curriculum,
            name="Mathematics",
            code="MATH",
            is_core=True,
        )
        StageSubject.objects.create(
            cambridge_stage=self.stage,
            subject=self.subject,
            weekly_lessons=5,
            is_core=True,
        )
        self.year_a = AcademicYear.objects.create(
            school=self.school_a,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
        )
        self.year_b = AcademicYear.objects.create(
            school=self.school_b,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
        )
        self.term_a = Term.objects.create(
            academic_year=self.year_a,
            term_number=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            is_current=True,
        )
        self.term_b = Term.objects.create(
            academic_year=self.year_b,
            term_number=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            is_current=True,
        )
        self.class_a = Classroom.objects.create(
            school=self.school_a,
            academic_year=self.year_a,
            term=self.term_a,
            cambridge_stage=self.stage,
            name="Ocean",
            code="OCEAN",
            capacity=25,
        )
        self.class_b = Classroom.objects.create(
            school=self.school_b,
            academic_year=self.year_b,
            term=self.term_b,
            cambridge_stage=self.stage,
            name="Forest",
            code="FOREST",
            capacity=25,
        )
        Enrollment.objects.create(
            student=self.student,
            classroom=self.class_a,
            academic_year=self.year_a,
            term=self.term_a,
            enrollment_date=date(2026, 1, 1),
        )

    def test_classroom_list_requires_authentication(self):
        response = self.client.get(reverse("classroom-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_list_all_classrooms(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse("classroom-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_student_only_sees_enrolled_classrooms(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.get(reverse("classroom-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.class_a.id))

    def test_student_cannot_access_other_school_classroom(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.get(reverse("classroom-detail", kwargs={"pk": self.class_b.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_can_read_curriculum_subjects(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.get(reverse("subject-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["code"], "MATH")

    def test_student_cannot_create_classroom(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.post(
            reverse("classroom-list"),
            {
                "school": str(self.school_a.id),
                "academic_year": str(self.year_a.id),
                "term": str(self.term_a.id),
                "cambridge_stage": str(self.stage.id),
                "name": "Unauthorized",
                "code": "UNAUTH",
                "capacity": 20,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

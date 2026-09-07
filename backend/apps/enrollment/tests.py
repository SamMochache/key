from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, Term
from apps.identity.models import User
from apps.schools.models import School
from apps.students.models import Student

from .models import Enrollment


class EnrollmentApiTests(APITestCase):
    def setUp(self):
        self.school_a = School.objects.create(name="School A", short_name="A", city="Nairobi")
        self.school_b = School.objects.create(name="School B", short_name="B", city="Nairobi")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="StrongPassword123!")
        self.student_user = User.objects.create_user(
            email="student@example.com", password="StrongPassword123!", first_name="Test", last_name="Student"
        )
        self.other_student_user = User.objects.create_user(
            email="other@example.com", password="StrongPassword123!", first_name="Other", last_name="Student"
        )
        self.student = Student.objects.create(
            user=self.student_user, school=self.school_a, admission_number="A-001",
            admission_date=date(2026, 1, 1), date_of_birth=date(2018, 1, 1), gender="male"
        )
        self.other_student = Student.objects.create(
            user=self.other_student_user, school=self.school_b, admission_number="B-001",
            admission_date=date(2026, 1, 1), date_of_birth=date(2018, 1, 1), gender="female"
        )
        curriculum = Curriculum.objects.create(name="Cambridge Primary", version="1.0")
        programme = Programme.objects.create(curriculum=curriculum, name="Cambridge Primary")
        stage = CambridgeStage.objects.create(programme=programme, name="Stage 3", stage_number=3, display_order=3)
        self.year_a = AcademicYear.objects.create(
            school=self.school_a, name="2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), is_current=True
        )
        self.year_b = AcademicYear.objects.create(
            school=self.school_b, name="2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), is_current=True
        )
        self.term_a = Term.objects.create(
            academic_year=self.year_a, term_number=1, start_date=date(2026, 1, 1), end_date=date(2026, 4, 30), is_current=True
        )
        self.term_b = Term.objects.create(
            academic_year=self.year_b, term_number=1, start_date=date(2026, 1, 1), end_date=date(2026, 4, 30), is_current=True
        )
        self.class_a = Classroom.objects.create(
            school=self.school_a, academic_year=self.year_a, term=self.term_a, cambridge_stage=stage,
            name="Ocean", code="OCEAN", capacity=25
        )
        self.class_b = Classroom.objects.create(
            school=self.school_b, academic_year=self.year_b, term=self.term_b, cambridge_stage=stage,
            name="Forest", code="FOREST", capacity=25
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, classroom=self.class_a, academic_year=self.year_a, term=self.term_a,
            enrollment_date=date(2026, 1, 5), status="ENROLLED"
        )
        self.list_url = reverse("enrollment-list")

    def test_unauthenticated_cannot_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_list_all_enrollments(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_student_sees_only_own_enrollment(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["student_name"], "Test Student")

    def test_student_cannot_access_other_school_enrollment(self):
        other = Enrollment.objects.create(
            student=self.other_student, classroom=self.class_b, academic_year=self.year_b, term=self.term_b,
            enrollment_date=date(2026, 1, 5), status="ENROLLED"
        )
        self.client.force_authenticate(self.student_user)
        response = self.client.get(reverse("enrollment-detail", kwargs={"pk": other.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_student_term_is_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            {
                "student": str(self.student.id), "classroom": str(self.class_a.id),
                "academic_year": str(self.year_a.id), "term": str(self.term_a.id),
                "enrollment_date": "2026-01-06", "status": "ENROLLED"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_classroom_filter_returns_its_students(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url, {"classroom": str(self.class_a.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.identity.models import User
from apps.schools.models import School
from apps.teachers.models import Department, Teacher

from .models import Student


class StudentApiTests(APITestCase):
    def setUp(self):
        self.school_a = School.objects.create(name="Key International School", short_name="KEY", city="Nairobi")
        self.school_b = School.objects.create(name="Partner School", short_name="PARTNER", city="Nairobi")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="StrongPassword123!")
        self.teacher_user = User.objects.create_user(
            email="teacher@example.com", password="StrongPassword123!", first_name="Test", last_name="Teacher"
        )
        self.student_user = User.objects.create_user(
            email="student@example.com", password="StrongPassword123!", first_name="Test", last_name="Student"
        )
        self.other_student_user = User.objects.create_user(
            email="other@example.com", password="StrongPassword123!", first_name="Other", last_name="Student"
        )
        department = Department.objects.create(school=self.school_a, name="Primary", code="PRI")
        Teacher.objects.create(
            user=self.teacher_user,
            school=self.school_a,
            employee_number="T-001",
            employment_type="FULL_TIME",
            employment_date=date(2025, 1, 1),
            department=department,
        )
        self.student = Student.objects.create(
            user=self.student_user, school=self.school_a, admission_number="KEY-001",
            admission_date=date(2026, 1, 1), date_of_birth=date(2015, 1, 1), gender="male",
        )
        self.other_student = Student.objects.create(
            user=self.other_student_user, school=self.school_b, admission_number="PARTNER-001",
            admission_date=date(2026, 1, 1), date_of_birth=date(2015, 2, 1), gender="female",
        )
        self.list_url = reverse("student-list")

    def test_list_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_list_all_students(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_teacher_only_sees_students_from_their_school(self):
        self.client.force_authenticate(self.teacher_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.student.id))

    def test_student_only_sees_themselves(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.student.id))

    def test_student_cannot_read_another_student(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.get(reverse("student-detail", kwargs={"pk": self.other_student.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_read_another_school_student(self):
        self.client.force_authenticate(self.teacher_user)
        response = self.client.get(reverse("student-detail", kwargs={"pk": self.other_student.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_can_filter_students_by_search(self):
        self.client.force_authenticate(self.teacher_user)
        response = self.client.get(self.list_url, {"search": "KEY-001"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_duplicate_admission_number_is_rejected_within_school(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            {
                "user": str(self.other_student_user.id), "school": str(self.school_a.id),
                "admission_number": "KEY-001", "admission_date": "2026-02-01",
                "date_of_birth": "2015-03-01", "gender": "male",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("admission_number", response.data)

    def test_student_cannot_create_student(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

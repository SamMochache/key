from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.identity.models import User
from apps.schools.models import School
from .models.department import Department
from .models.teacher import Teacher


class TeacherApiTests(APITestCase):
    def setUp(self):
        self.school_a = School.objects.create(name="Key International School", short_name="KEY", city="Nairobi")
        self.school_b = School.objects.create(name="Partner School", short_name="PARTNER", city="Nairobi")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="StrongPassword123!")
        self.teacher_user = User.objects.create_user(email="teacher@example.com", password="StrongPassword123!", first_name="Test", last_name="Teacher")
        self.other_teacher_user = User.objects.create_user(email="other@example.com", password="StrongPassword123!", first_name="Other", last_name="Teacher")
        self.student_user = User.objects.create_user(email="student@example.com", password="StrongPassword123!", first_name="Test", last_name="Student")
        department_a = Department.objects.create(school=self.school_a, name="Primary", code="PRI")
        department_b = Department.objects.create(school=self.school_b, name="Primary", code="PRI")
        self.teacher = Teacher.objects.create(user=self.teacher_user, school=self.school_a, employee_number="T-001", employment_type="FULL_TIME", employment_date=date(2025, 1, 1), department=department_a)
        self.other_teacher = Teacher.objects.create(user=self.other_teacher_user, school=self.school_b, employee_number="T-001", employment_type="FULL_TIME", employment_date=date(2025, 1, 1), department=department_b)
        self.list_url = reverse("teacher-list")

    def test_list_requires_authentication(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_list_all_teachers(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_teacher_only_sees_own_school(self):
        self.client.force_authenticate(self.teacher_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.teacher.id))

    def test_teacher_cannot_read_other_school_teacher(self):
        self.client.force_authenticate(self.teacher_user)
        response = self.client.get(reverse("teacher-detail", kwargs={"pk": self.other_teacher.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_is_scoped_to_school(self):
        self.client.force_authenticate(self.teacher_user)
        response = self.client.get(self.list_url, {"search": "T-001"})
        self.assertEqual(response.data["count"], 1)

    def test_student_can_read_teachers_in_own_school(self):
        from apps.students.models import Student
        Student.objects.create(user=self.student_user, school=self.school_a, admission_number="S-001", admission_date=date(2026, 1, 1), date_of_birth=date(2016, 1, 1), gender="male")
        self.client.force_authenticate(self.student_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_teacher_cannot_create_teacher(self):
        self.client.force_authenticate(self.teacher_user)
        response = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

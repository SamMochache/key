from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.identity.models import User
from apps.students.models import Student

from .models import School


class SchoolApiTests(APITestCase):
    def setUp(self):
        self.school_a = School.objects.create(
            name="Key International School",
            short_name="KEY",
            city="Nairobi",
        )
        self.school_b = School.objects.create(
            name="Partner School",
            short_name="PARTNER",
            city="Nairobi",
        )

        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPassword123!",
        )
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Student",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            school=self.school_a,
            admission_number="KEY-001",
            admission_date=date(2026, 1, 1),
            date_of_birth=date(2015, 1, 1),
            gender="male",
        )

        self.list_url = reverse("school-list")

    def test_school_list_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_list_all_schools(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_admin_can_create_school(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                "name": "New Partner School",
                "short_name": "NEW",
                "city": "Nairobi",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(School.objects.filter(short_name="NEW").exists())

    def test_student_only_sees_their_school(self):
        self.client.force_authenticate(self.student_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.school_a.id))

    def test_student_cannot_read_another_school(self):
        self.client.force_authenticate(self.student_user)

        response = self.client.get(
            reverse("school-detail", kwargs={"pk": self.school_b.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_create_school(self):
        self.client.force_authenticate(self.student_user)

        response = self.client.post(
            self.list_url,
            {
                "name": "Unauthorized School",
                "short_name": "UNAUTH",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(School.objects.filter(short_name="UNAUTH").exists())

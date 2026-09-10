from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, Term
from apps.enrollment.models import Enrollment
from apps.identity.models import User
from apps.schools.models import School, SchoolAdministrator
from apps.students.models import Student

from .models import Parent, ParentStudentRelationship


class ParentAuthorizationTests(APITestCase):
    def setUp(self):
        self.school_a = School.objects.create(name="School A", short_name="PA", city="Nairobi")
        self.school_b = School.objects.create(name="School B", short_name="PB", city="Nairobi")

        admin_user = User.objects.create_user(
            email="admin-a@example.com",
            password="StrongPassword123!",
            first_name="School",
            last_name="Admin",
        )
        SchoolAdministrator.objects.create(user=admin_user, school=self.school_a)
        self.admin = admin_user

        self.student_user = User.objects.create_user(
            email="student-b@example.com",
            password="StrongPassword123!",
            first_name="Student",
            last_name="B",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            school=self.school_b,
            admission_number="B-001",
            admission_date=date(2026, 1, 1),
            date_of_birth=date(2018, 1, 1),
            gender="male",
        )

        curriculum = Curriculum.objects.create(name="Primary", version="1.0")
        programme = Programme.objects.create(curriculum=curriculum, name="Primary")
        stage = CambridgeStage.objects.create(
            programme=programme,
            name="Stage 3",
            stage_number=3,
            display_order=3,
        )
        year = AcademicYear.objects.create(
            school=self.school_b,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
        )
        term = Term.objects.create(
            academic_year=year,
            term_number=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            is_current=True,
        )
        classroom = Classroom.objects.create(
            school=self.school_b,
            academic_year=year,
            term=term,
            cambridge_stage=stage,
            name="Forest",
            code="FOREST-B",
            capacity=25,
        )
        Enrollment.objects.create(
            student=self.student,
            classroom=classroom,
            academic_year=year,
            term=term,
            enrollment_date=date(2026, 1, 1),
        )

        other_parent_user = User.objects.create_user(
            email="parent-b@example.com",
            password="StrongPassword123!",
            first_name="Parent",
            last_name="B",
        )
        self.other_parent = Parent.objects.create(user=other_parent_user, school=self.school_b)
        ParentStudentRelationship.objects.create(parent=self.other_parent, student=self.student)

    def test_school_admin_cannot_list_other_school_parents(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse("parent-management"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_school_admin_cannot_create_parent_for_other_school(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse("parent-management"),
            {
                "first_name": "New",
                "last_name": "Parent",
                "email": "new-parent@example.com",
                "password": "StrongPassword123!",
                "school": str(self.school_b.id),
                "student": str(self.student.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_school_admin_cannot_update_other_school_parent(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            reverse("parent-management"),
            {"id": str(self.other_parent.id), "is_active": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parent_children_are_limited_to_authenticated_parent(self):
        parent_user = self.other_parent.user
        self.client.force_authenticate(parent_user)
        response = self.client.get(reverse("parent-children"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.student.id))

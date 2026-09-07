from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.identity.models import User
from apps.schools.models import School
from apps.teachers.models import Department, Teacher

from .models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, Term


class ClassroomManagementApiTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name="School A", short_name="A", city="Nairobi")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="StrongPassword123!")
        curriculum = Curriculum.objects.create(name="Cambridge Primary", version="1.0")
        programme = Programme.objects.create(curriculum=curriculum, name="Cambridge Primary")
        self.stage = CambridgeStage.objects.create(programme=programme, name="Stage 3", stage_number=3, display_order=3)
        self.year = AcademicYear.objects.create(school=self.school, name="2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), is_current=True)
        self.term = Term.objects.create(academic_year=self.year, term_number=1, start_date=date(2026, 1, 1), end_date=date(2026, 4, 30), is_current=True)
        department = Department.objects.create(school=self.school, name="Primary", code="PRI")
        teacher_user = User.objects.create_user(email="teacher@example.com", password="StrongPassword123!", first_name="Jane", last_name="Mwangi")
        self.teacher = Teacher.objects.create(user=teacher_user, school=self.school, employee_number="T-001", employment_type="FULL_TIME", employment_date=date(2025, 1, 1), status="ACTIVE", department=department)

    def authenticate(self):
        self.client.force_authenticate(self.admin)

    def payload(self, **extra):
        return {
            "school": str(self.school.id),
            "academic_year": str(self.year.id),
            "term": str(self.term.id),
            "cambridge_stage": str(self.stage.id),
            "name": "Grade 4A",
            "code": "G4A",
            "capacity": 30,
            **extra,
        }

    def test_admin_can_create_class_with_primary_teacher(self):
        self.authenticate()
        response = self.client.post(reverse("classroom-list"), self.payload(primary_teacher=str(self.teacher.id)), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["primary_teacher_id"], str(self.teacher.id))
        self.assertEqual(response.data["primary_teacher_name"], "Jane Mwangi")

    def test_admin_can_update_class_teacher(self):
        self.authenticate()
        classroom = Classroom.objects.create(school=self.school, academic_year=self.year, term=self.term, cambridge_stage=self.stage, name="Grade 4A", code="G4A", capacity=30)
        response = self.client.patch(reverse("classroom-detail", kwargs={"pk": classroom.pk}), {"primary_teacher": str(self.teacher.id)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        classroom.refresh_from_db()
        assignment = classroom.teacher_assignments.get(role="PRIMARY", is_active=True)
        self.assertEqual(assignment.teacher_id, self.teacher.id)

    def test_delete_class_deactivates_it(self):
        self.authenticate()
        classroom = Classroom.objects.create(school=self.school, academic_year=self.year, term=self.term, cambridge_stage=self.stage, name="Grade 4A", code="G4A", capacity=30)
        response = self.client.delete(reverse("classroom-detail", kwargs={"pk": classroom.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        classroom.refresh_from_db()
        self.assertFalse(classroom.is_active)

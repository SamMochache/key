import inspect
from datetime import date

from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIClient

from apps.academics.models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, Term
from apps.assessments.serializers import AssessmentSerializer
from apps.attendance.serializers import AttendanceRecordSerializer, AttendanceRegisterSerializer
from apps.communication.serializers import CommunicationContactSerializer, CommunicationMessageSerializer
from apps.enrollment.serializers import EnrollmentSerializer
from apps.identity.models import User
from apps.lessons.serializers import LessonSessionSerializer
from apps.portfolio.serializers import ArtifactSerializer, PortfolioItemSerializer, PortfolioSerializer
from apps.schools.models import School, SchoolAdministrator
from apps.schools.serializers import SchoolSerializer
from apps.students.serializers import StudentSerializer
from apps.teachers.serializers import DepartmentSerializer, TeacherSerializer, TeacherSubjectSerializer
from apps.timetables.models.period import Period
from apps.timetables.models.timetable import Timetable
from apps.timetables.serializers import PeriodSerializer, TimetableEntrySerializer, TimetableSerializer


SERIALIZER_CLASSES = [
    AssessmentSerializer,
    AttendanceRecordSerializer,
    AttendanceRegisterSerializer,
    CommunicationContactSerializer,
    CommunicationMessageSerializer,
    EnrollmentSerializer,
    LessonSessionSerializer,
    ArtifactSerializer,
    PortfolioItemSerializer,
    PortfolioSerializer,
    SchoolSerializer,
    StudentSerializer,
    DepartmentSerializer,
    TeacherSerializer,
    TeacherSubjectSerializer,
    PeriodSerializer,
    TimetableSerializer,
    TimetableEntrySerializer,
]


class SerializerContractTests(TestCase):
    def test_model_serializers_build_all_declared_fields(self):
        """Unknown ModelSerializer fields must fail in CI, not in production traffic."""
        from apps.academics.serializers import (
            AcademicYearSerializer,
            CambridgeStageSerializer,
            ClassroomSerializer,
            CurriculumSerializer,
            MontessoriLevelSerializer,
            ProgrammeSerializer,
            StageSubjectSerializer,
            SubjectSerializer,
            TermSerializer,
        )

        serializers_to_check = [
            AcademicYearSerializer,
            CambridgeStageSerializer,
            ClassroomSerializer,
            CurriculumSerializer,
            MontessoriLevelSerializer,
            ProgrammeSerializer,
            StageSubjectSerializer,
            SubjectSerializer,
            TermSerializer,
            *SERIALIZER_CLASSES,
        ]
        for serializer_class in serializers_to_check:
            with self.subTest(serializer=serializer_class.__name__):
                serializer = serializer_class()
                self.assertTrue(serializer.fields)


class BackendTenantSmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.school_a = School.objects.create(name="School A", short_name="A")
        self.school_b = School.objects.create(name="School B", short_name="B")

        self.admin_user = User.objects.create_user(
            email="admin-a@test.local",
            password="TestPass123!",
            first_name="Admin",
            last_name="A",
        )
        SchoolAdministrator.objects.create(user=self.admin_user, school=self.school_a)

        self.year_a = AcademicYear.objects.create(
            school=self.school_a,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
            is_active=True,
        )
        self.year_b = AcademicYear.objects.create(
            school=self.school_b,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
            is_active=True,
        )
        self.term_a = Term.objects.create(
            academic_year=self.year_a,
            term_number=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            is_current=True,
            is_active=True,
        )
        self.term_b = Term.objects.create(
            academic_year=self.year_b,
            term_number=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            is_current=True,
            is_active=True,
        )
        curriculum = Curriculum.objects.create(name="Cambridge")
        programme = Programme.objects.create(curriculum=curriculum, name="Primary")
        self.stage = CambridgeStage.objects.create(
            programme=programme,
            name="Primary Stage",
            stage_number=1,
            display_order=1,
        )

    def test_classroom_list_returns_annotated_counts(self):
        Classroom.objects.create(
            school=self.school_a,
            academic_year=self.year_a,
            term=self.term_a,
            cambridge_stage=self.stage,
            name="Year 4",
            code="Y4",
            capacity=30,
            is_active=True,
        )
        self.client.force_authenticate(self.admin_user)
        response = self.client.get("/api/classrooms/?active=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student_count"], 0)
        self.assertEqual(response.data[0]["subject_count"], 0)

    def test_school_admin_timetable_list_is_tenant_scoped(self):
        Timetable.objects.create(
            school=self.school_a,
            academic_year=self.year_a,
            term=self.term_a,
            name="School A timetable",
            version=1,
            status="PUBLISHED",
            effective_from=date(2026, 1, 1),
        )
        Timetable.objects.create(
            school=self.school_b,
            academic_year=self.year_b,
            term=self.term_b,
            name="School B timetable",
            version=1,
            status="PUBLISHED",
            effective_from=date(2026, 1, 1),
        )
        self.client.force_authenticate(self.admin_user)
        response = self.client.get("/api/timetables/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["school"], str(self.school_a.id))


class PlatformAdminContractTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.platform_user = User.objects.create_user(
            email="platform-admin@test.local",
            password="TestPass123!",
            first_name="Platform",
            last_name="Admin",
        )
        self.platform_user.is_staff = True
        self.platform_user.save(update_fields=["is_staff"])

        self.school_admin = User.objects.create_user(
            email="school-admin@test.local",
            password="TestPass123!",
            first_name="School",
            last_name="Admin",
        )
        self.school = School.objects.create(name="School A", short_name="A")
        SchoolAdministrator.objects.create(user=self.school_admin, school=self.school)

    def test_platform_admin_current_user_has_platform_flag_and_no_school(self):
        self.client.force_authenticate(self.platform_user)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "admin")
        self.assertTrue(response.data["platform_admin"])
        self.assertNotIn("school_id", response.data)

    def test_school_admin_current_user_is_not_platform_admin(self):
        self.client.force_authenticate(self.school_admin)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "admin")
        self.assertNotIn("platform_admin", response.data)
        self.assertEqual(response.data["school_id"], str(self.school.id))

    def test_platform_admin_can_list_all_schools(self):
        School.objects.create(name="School B", short_name="B")
        self.client.force_authenticate(self.platform_user)
        response = self.client.get("/api/schools/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_school_admin_only_sees_own_school(self):
        School.objects.create(name="School B", short_name="B")
        self.client.force_authenticate(self.school_admin)
        response = self.client.get("/api/schools/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.school.id))

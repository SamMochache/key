from datetime import date

from django.core.management import call_command
from django.test import TestCase

from apps.academics.models import AcademicYear, Term
from apps.assessments.models import AINarrativeReport
from apps.identity.models import User
from apps.parents.models import Parent, ParentStudentRelationship
from apps.schools.models import School
from apps.students.models import Student
from core.constants.student import Gender


class RepairDemoIdentityMappingTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Nairobi International Montessori & STEM Academy",
            short_name="NIMSA-DEMO",
            email="admin@key-demo.test",
            phone_number="+254700000001",
            address="Westlands, Nairobi",
            city="Nairobi",
            country="Kenya",
            timezone="Africa/Nairobi",
            is_active=True,
        )
        self.admin = User.objects.create(
            email="admin@key-demo.test",
            first_name="Grace",
            last_name="Wanjiku",
            is_active=True,
        )
        self.parent_user = User.objects.create(
            email="parent@keydemo.test",
            first_name="Daniel",
            last_name="Otieno",
            is_active=True,
        )
        self.parent = Parent.objects.create(
            user=self.parent_user,
            school=self.school,
            is_active=True,
        )
        self.legacy_user = User.objects.create(
            email="student1@keydemo.test",
            first_name="Amina",
            last_name="Otieno",
            is_active=True,
        )
        self.canonical_user = User.objects.create(
            email="student01@key-demo.test",
            first_name="Amina",
            last_name="Otieno",
            is_active=True,
        )
        self.legacy_student = Student.objects.create(
            user=self.legacy_user,
            school=self.school,
            admission_number="LEGACY-001",
            admission_date=date(2026, 1, 5),
            date_of_birth=date(2015, 3, 14),
            gender=Gender.FEMALE,
        )
        self.canonical_student = Student.objects.create(
            user=self.canonical_user,
            school=self.school,
            admission_number="DEMO-001",
            admission_date=date(2026, 1, 5),
            date_of_birth=date(2015, 3, 14),
            gender=Gender.FEMALE,
        )
        ParentStudentRelationship.objects.create(
            parent=self.parent,
            student=self.legacy_student,
            can_view_reports=True,
            is_primary_contact=True,
            is_active=True,
        )
        year = AcademicYear.objects.create(
            school=self.school,
            name="2026",
            start_date=date(2026, 1, 5),
            end_date=date(2026, 12, 11),
            is_current=True,
            is_active=True,
        )
        term = Term.objects.create(
            academic_year=year,
            term_number=3,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 11),
            is_current=True,
            is_active=True,
        )
        AINarrativeReport.objects.create(
            student=self.legacy_student,
            academic_year=year,
            term=term,
            generated_content={"summary": "Amina is progressing well."},
            source_data_snapshot={},
            status=AINarrativeReport.Status.PUBLISHED,
            generated_by=self.admin,
        )

    def test_repair_moves_relationship_and_non_conflicting_report(self):
        call_command("repair_demo_identity_mapping", "--apply")

        relationship = ParentStudentRelationship.objects.get(parent=self.parent)
        self.assertEqual(relationship.student_id, self.canonical_student.id)
        self.assertTrue(relationship.can_view_reports)
        self.assertFalse(Student.objects.get(pk=self.legacy_student.pk).is_active)
        self.assertFalse(User.objects.get(pk=self.legacy_user.pk).is_active)

        report = AINarrativeReport.objects.get()
        self.assertEqual(report.student_id, self.canonical_student.id)

    def test_dry_run_does_not_change_identity_graph(self):
        call_command("repair_demo_identity_mapping")

        relationship = ParentStudentRelationship.objects.get(parent=self.parent)
        self.assertEqual(relationship.student_id, self.legacy_student.id)
        self.assertTrue(Student.objects.get(pk=self.legacy_student.pk).is_active)
        self.assertTrue(User.objects.get(pk=self.legacy_user.pk).is_active)
        report = AINarrativeReport.objects.get()
        self.assertEqual(report.student_id, self.legacy_student.id)

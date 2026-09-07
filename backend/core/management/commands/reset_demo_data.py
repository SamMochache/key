from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.academics.models import AcademicYear, CambridgeStage, Classroom, Curriculum, Programme, Subject, Term
from apps.communication.models import CommunicationMessage
from apps.identity.models import User
from apps.notifications.models import Notification
from apps.parents.models import Parent, ParentStudentRelationship
from apps.schools.models import School
from apps.students.models import Student
from apps.teachers.models import Department, Teacher
from core.constants.student import Gender
from core.constants.teacher import EmploymentType, TeacherStatus


class Command(BaseCommand):
    help = "Destructively reset the development database and load a complete KEY demo dataset."

    PASSWORDS = {
        "admin@keydemo.test": "KeyAdmin2026!",
        "teacher@keydemo.test": "KeyTeacher2026!",
        "parent@keydemo.test": "KeyParent2026!",
        "student1@keydemo.test": "KeyStudent12026!",
        "student2@keydemo.test": "KeyStudent22026!",
        "student3@keydemo.test": "KeyStudent32026!",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required: confirms that all database data may be deleted.",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError(
                "This command deletes all database data. Re-run with --confirm."
            )

        self.stdout.write(self.style.WARNING("Resetting the KEY database..."))

        # Flush removes rows but preserves the migration/schema history.
        call_command("flush", interactive=False, reset_sequences=True, verbosity=0)

        with transaction.atomic():
            school = School.objects.create(
                name="Key International School",
                short_name="KEY",
                email="admin@keydemo.test",
                phone_number="+254700000000",
                address="Nairobi, Kenya",
                city="Nairobi",
                country="Kenya",
                timezone="Africa/Nairobi",
                is_active=True,
            )

            admin = User.objects.create_superuser(
                email="admin@keydemo.test",
                password=self.PASSWORDS["admin@keydemo.test"],
                first_name="KEY",
                last_name="Administrator",
            )

            teacher_user = User.objects.create_user(
                email="teacher@keydemo.test",
                password=self.PASSWORDS["teacher@keydemo.test"],
                first_name="Grace",
                last_name="Mwangi",
                phone_number="+254711111111",
            )
            department = Department.objects.create(
                school=school,
                name="STEM & Technology",
                code="STEM",
                description="Science, technology, engineering and mathematics.",
            )
            teacher = Teacher.objects.create(
                user=teacher_user,
                school=school,
                employee_number="TCH-001",
                employment_type=EmploymentType.FULL_TIME,
                employment_date=date(2024, 1, 8),
                status=TeacherStatus.ACTIVE,
                department=department,
            )

            parent_user = User.objects.create_user(
                email="parent@keydemo.test",
                password=self.PASSWORDS["parent@keydemo.test"],
                first_name="Daniel",
                last_name="Otieno",
                phone_number="+254722222222",
            )
            parent = Parent.objects.create(user=parent_user, school=school)

            curriculum = Curriculum.objects.create(
                name="Cambridge Primary",
                version="2026",
                description="Demo Cambridge Primary curriculum for KEY testing.",
            )
            programme = Programme.objects.create(
                curriculum=curriculum,
                name="Cambridge Primary",
                description="Primary programme used by the demo school.",
                display_order=1,
            )
            stage = CambridgeStage.objects.create(
                programme=programme,
                name="Year 5",
                stage_number=5,
                display_order=5,
            )
            subjects = [
                Subject.objects.create(curriculum=curriculum, name="Mathematics", code="MATH", display_order=1),
                Subject.objects.create(curriculum=curriculum, name="Science", code="SCI", display_order=2),
                Subject.objects.create(curriculum=curriculum, name="Computing", code="COMP", display_order=3),
                Subject.objects.create(curriculum=curriculum, name="English", code="ENG", display_order=4),
            ]

            academic_year = AcademicYear.objects.create(
                school=school,
                name="2026",
                start_date=date(2026, 1, 5),
                end_date=date(2026, 12, 4),
                is_current=True,
                is_active=True,
            )
            term = Term.objects.create(
                academic_year=academic_year,
                term_number=3,
                start_date=date(2026, 9, 1),
                end_date=date(2026, 12, 4),
                is_current=True,
                is_active=True,
            )
            classroom = Classroom.objects.create(
                school=school,
                academic_year=academic_year,
                term=term,
                cambridge_stage=stage,
                name="Year 5 Blue",
                code="Y5-B",
                capacity=30,
                is_active=True,
            )

            student_rows = [
                ("student1@keydemo.test", "Amina", "Otieno", "STU-001", date(2015, 3, 14), Gender.FEMALE),
                ("student2@keydemo.test", "Brian", "Kamau", "STU-002", date(2015, 7, 22), Gender.MALE),
                ("student3@keydemo.test", "Chloe", "Njeri", "STU-003", date(2015, 11, 5), Gender.FEMALE),
            ]
            students = []
            for email, first_name, last_name, admission, dob, gender in student_rows:
                user = User.objects.create_user(
                    email=email,
                    password=self.PASSWORDS[email],
                    first_name=first_name,
                    last_name=last_name,
                )
                student = Student.objects.create(
                    user=user,
                    school=school,
                    admission_number=admission,
                    admission_date=date(2026, 1, 5),
                    date_of_birth=dob,
                    gender=gender,
                    nationality="Kenyan",
                    is_active=True,
                )
                students.append(student)

            ParentStudentRelationship.objects.create(
                parent=parent,
                student=students[0],
                relationship=ParentStudentRelationship.Relationship.PARENT,
                can_view_reports=True,
                is_primary_contact=True,
                is_active=True,
            )
            ParentStudentRelationship.objects.create(
                parent=parent,
                student=students[1],
                relationship=ParentStudentRelationship.Relationship.PARENT,
                can_view_reports=True,
                is_primary_contact=False,
                is_active=True,
            )

            CommunicationMessage.objects.create(
                school=school,
                sender=teacher_user,
                recipient=parent_user,
                subject="Welcome to the new term",
                body="Welcome. Amina and Brian are ready for the new learning term.",
            )
            CommunicationMessage.objects.create(
                school=school,
                sender=parent_user,
                recipient=teacher_user,
                subject="Re: Welcome to the new term",
                body="Thank you. We are looking forward to a great term.",
            )

            Notification.objects.create(
                school=school,
                recipient=teacher_user,
                notification_type=Notification.Type.MESSAGE,
                title="New message from Daniel Otieno",
                body="Thank you. We are looking forward to a great term.",
                link="/communication",
            )
            Notification.objects.create(
                school=school,
                recipient=parent_user,
                notification_type=Notification.Type.SYSTEM,
                title="Welcome to KEY",
                body="Your demo parent account is ready.",
                link="/",
            )
            Notification.objects.create(
                school=school,
                recipient=student_user if False else students[0].user,
                notification_type=Notification.Type.ASSESSMENT,
                title="New assessment available",
                body="Your Computing assessment is ready to view.",
                link="/assessments",
            )

        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully."))
        self.stdout.write("")
        self.stdout.write("TEST ACCOUNTS")
        self.stdout.write("==============")
        for email, password in self.PASSWORDS.items():
            self.stdout.write(f"{email:<28} {password}")
        self.stdout.write("")
        self.stdout.write(f"School: {school.name}")
        self.stdout.write(f"Class: {classroom.name}")
        self.stdout.write(f"Teacher: {teacher.user.email}")
        self.stdout.write(f"Students: {len(students)}")
        self.stdout.write(f"Subjects: {len(subjects)}")

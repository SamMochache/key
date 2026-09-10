import os

from django.core.management.base import BaseCommand, CommandError

from apps.identity.models import User
from apps.parents.models import Parent, ParentStudentRelationship
from apps.schools.models import School
from apps.students.models import Student


DEMO_SHORT_NAME = "NIMSA-DEMO"
PARENT_EMAIL = "parent@key-demo.test"


class Command(BaseCommand):
    help = "Create the canonical KEY demo parent account and report access for Amina and Brian."

    def handle(self, *args, **options):
        school = School.objects.filter(short_name=DEMO_SHORT_NAME).first()
        if school is None:
            raise CommandError("KEY demo school was not found. Run seed_demo first.")

        students = list(
            Student.objects.filter(
                school=school,
                user__email__in=[
                    "student01@key-demo.test",
                    "student02@key-demo.test",
                ],
                is_active=True,
            ).select_related("user")
        )
        if len(students) != 2:
            raise CommandError(
                "Expected canonical Amina and Brian student accounts. Run seed_demo --reset first."
            )

        parent_user, _ = User.objects.update_or_create(
            email=PARENT_EMAIL,
            defaults={
                "first_name": "Daniel",
                "last_name": "Otieno",
                "phone_number": "+254722222222",
                "status": "ACTIVE",
                "is_active": True,
                "preferred_language": "en",
                "timezone": "Africa/Nairobi",
            },
        )
        parent_password = os.environ.get("KEY_DEMO_PARENT_PASSWORD")
        if parent_password:
            parent_user.set_password(parent_password)
            parent_user.save(update_fields=["password", "is_active", "status"])
        else:
            parent_user.save(update_fields=["is_active", "status"])
            self.stdout.write(
                self.style.WARNING(
                    "KEY_DEMO_PARENT_PASSWORD was not set; existing password was preserved."
                )
            )

        parent, _ = Parent.objects.update_or_create(
            user=parent_user,
            defaults={"school": school, "is_active": True},
        )

        for index, student in enumerate(students):
            ParentStudentRelationship.objects.update_or_create(
                parent=parent,
                student=student,
                defaults={
                    "relationship": ParentStudentRelationship.Relationship.PARENT,
                    "can_view_reports": True,
                    "is_primary_contact": index == 0,
                    "is_active": True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Canonical demo parent access is ready: {PARENT_EMAIL}"
            )
        )
        self.stdout.write(
            "Linked students: "
            + ", ".join(student.user.full_name for student in students)
        )

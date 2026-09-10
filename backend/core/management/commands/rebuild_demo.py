from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.assessments.models import AINarrativeReport
from apps.identity.models import User
from apps.parents.models import Parent, ParentStudentRelationship
from apps.schools.models import School
from apps.students.models import Student


DEMO_SHORT_NAME = "NIMSA-DEMO"
PARENT_EMAIL = "parent@key-demo.test"
PARENT_PASSWORD = "DemoParent123!"


class Command(BaseCommand):
    help = (
        "Flush the entire database and rebuild the KEY demo dataset from the "
        "current migrations and seed commands. DEVELOPMENT/DEMO USE ONLY."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm-reset",
            action="store_true",
            help="Required confirmation because this permanently removes ALL database data.",
        )

    def handle(self, *args, **options):
        if not options["confirm_reset"]:
            raise CommandError(
                "This command deletes ALL database data while preserving the schema. "
                "Run with --confirm-reset only against the intended demo/development database."
            )

        self.stdout.write(self.style.WARNING("Flushing ALL database data..."))
        management.call_command("flush", interactive=False, verbosity=0)
        self.stdout.write(self.style.SUCCESS("Database data cleared; tables/schema preserved."))

        self.stdout.write("Seeding the canonical demo school...")
        management.call_command("seed_demo", verbosity=1)

        school = School.objects.get(short_name=DEMO_SHORT_NAME)
        students = list(
            Student.objects.filter(
                school=school,
                user__email__in=[
                    "student01@key-demo.test",
                    "student02@key-demo.test",
                ],
            ).select_related("user")
        )
        if len(students) != 2:
            raise CommandError("Fresh seed did not create canonical Amina and Brian students.")

        admin = User.objects.get(email="admin@key-demo.test")
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
        parent_user.set_password(PARENT_PASSWORD)
        parent_user.save(update_fields=["password", "is_active", "status"])

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

        # Create real, published AI reports against the exact freshly created
        # Student rows. This deliberately avoids names/email lookups later.
        year = school.academic_years.get(name="2026")
        term = year.terms.get(term_number=1)
        now = timezone.now()
        for student in students:
            narrative = {
                "overall_progress": (
                    f"{student.user.first_name} has made a positive start to the 2026 school year, "
                    "with strong participation in the published learning activities."
                ),
                "strengths": (
                    "Consistent engagement and strong performance across the published assessment results."
                ),
                "areas_for_development": (
                    "Continue building a broad portfolio of learning evidence and reflections."
                ),
                "suggested_next_steps": (
                    "Participate actively in classroom projects and add evidence of learning to the portfolio."
                ),
                "teacher_review_note": "Positive progress noted during Term 1.",
            }
            AINarrativeReport.objects.update_or_create(
                student=student,
                academic_year=year,
                term=term,
                defaults={
                    "generated_content": narrative,
                    "edited_content": narrative,
                    "source_data_snapshot": {
                        "student_id": str(student.id),
                        "student_name": student.user.full_name,
                        "academic_year": year.name,
                        "term_number": term.term_number,
                        "grounded_in_published_records": True,
                    },
                    "status": AINarrativeReport.Status.PUBLISHED,
                    "generated_by": admin,
                    "reviewed_by": admin,
                    "published_by": admin,
                    "model_used": "demo-seed-grounded",
                    "reviewed_at": now,
                    "published_at": now,
                },
            )

        self.stdout.write(self.style.SUCCESS("\nClean KEY demo database rebuilt successfully."))
        self.stdout.write("Canonical accounts:")
        self.stdout.write("  Admin: admin@key-demo.test / DemoAdmin123!")
        self.stdout.write("  Parent: parent@key-demo.test / DemoParent123!")
        self.stdout.write("  Students: student01@key-demo.test … student16@key-demo.test / DemoStudent123!")
        self.stdout.write("  Parent learners: Amina Otieno, Brian Kamau")
        self.stdout.write("  Published Term 1 AI reports: Amina Otieno, Brian Kamau")

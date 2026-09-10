from django.core.management.base import BaseCommand
from django.db import transaction

from apps.assessments.models import AINarrativeReport
from apps.parents.models import ParentStudentRelationship
from apps.students.models import Student
from apps.identity.models import User


class Command(BaseCommand):
    help = "Reconcile legacy @keydemo.test student identities with the canonical @key-demo.test demo students."

    # PR #19 used student1@keydemo.test, student2@keydemo.test, etc.
    # The current seed uses zero-padded addresses under @key-demo.test.
    # Email is used deliberately here: it is the identity key, not a name match.
    LEGACY_TO_CANONICAL = {
        f"student{i}@keydemo.test": f"student{i:02d}@key-demo.test"
        for i in range(1, 17)
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the reconciliation. Without this flag the command only reports what would change.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        changed_relationships = 0
        deactivated_students = 0
        skipped = 0

        for legacy_email, canonical_email in self.LEGACY_TO_CANONICAL.items():
            legacy_user = User.objects.filter(email__iexact=legacy_email).first()
            canonical_user = User.objects.filter(email__iexact=canonical_email).first()

            if legacy_user is None:
                continue
            if canonical_user is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"SKIP {legacy_email}: canonical account {canonical_email} does not exist."
                    )
                )
                skipped += 1
                continue

            legacy_student = Student.objects.filter(user=legacy_user).first()
            canonical_student = Student.objects.filter(user=canonical_user).first()
            if legacy_student is None or canonical_student is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"SKIP {legacy_email}: both linked Student profiles are required."
                    )
                )
                skipped += 1
                continue

            relationships = list(
                ParentStudentRelationship.objects.filter(student=legacy_student)
            )
            if relationships:
                self.stdout.write(
                    f"{legacy_email} -> {canonical_email}: {len(relationships)} parent relationship(s)"
                )

            if not apply_changes:
                continue

            with transaction.atomic():
                for relationship in relationships:
                    duplicate = ParentStudentRelationship.objects.filter(
                        parent=relationship.parent,
                        student=canonical_student,
                    ).exclude(pk=relationship.pk).first()
                    if duplicate:
                        # The canonical relationship already exists. Preserve the
                        # canonical row and remove only the obsolete duplicate edge.
                        relationship.delete()
                    else:
                        relationship.student = canonical_student
                        relationship.save(update_fields=["student", "updated_at"])
                    changed_relationships += 1

                # Reports are already canonical in the current workflow. Do not
                # move them by name or overwrite a canonical report. If an old
                # report exists, report it so it can be handled explicitly.
                old_report_count = AINarrativeReport.objects.filter(
                    student=legacy_student
                ).count()
                canonical_report_count = AINarrativeReport.objects.filter(
                    student=canonical_student
                ).count()
                if old_report_count and canonical_report_count:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Reports: legacy={old_report_count}, canonical={canonical_report_count}; left untouched."
                        )
                    )
                elif old_report_count:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Reports: {old_report_count} legacy report(s) remain attached to {legacy_email}."
                        )
                    )

                # Keep historical records intact but prevent the obsolete login
                # and profile from being mistaken for the canonical learner.
                legacy_student.is_active = False
                legacy_student.save(update_fields=["is_active", "updated_at"])
                legacy_user.is_active = False
                legacy_user.save(update_fields=["is_active", "updated_at"])
                deactivated_students += 1

        if apply_changes:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Reconciliation complete: {changed_relationships} relationship(s) processed; "
                    f"{deactivated_students} legacy student account(s) deactivated; {skipped} skipped."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run only. Re-run with --apply to reconcile the reported relationships and deactivate legacy student accounts."
                )
            )

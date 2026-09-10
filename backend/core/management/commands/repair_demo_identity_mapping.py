from django.core.management.base import BaseCommand
from django.db import transaction

from apps.assessments.models import AINarrativeReport
from apps.parents.models import Parent, ParentStudentRelationship
from apps.students.models import Student
from apps.identity.models import User


class Command(BaseCommand):
    help = "Reconcile legacy @keydemo.test demo identities with canonical @key-demo.test identities."

    # PR #19 used these legacy addresses. The current demo seed uses zero-padded
    # student addresses under @key-demo.test. Email is the deliberate migration
    # key; names are never used to identify or merge people.
    LEGACY_TO_CANONICAL = {
        f"student{i}@keydemo.test": f"student{i:02d}@key-demo.test"
        for i in range(1, 17)
    }
    LEGACY_PARENT_EMAIL = "parent@keydemo.test"
    CANONICAL_PARENT_EMAIL = "parent@key-demo.test"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the reconciliation. Without this flag the command only reports what would change.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        changed_relationships = 0
        migrated_reports = 0
        deactivated_students = 0
        deactivated_parents = 0
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
            old_reports = list(
                AINarrativeReport.objects.filter(student=legacy_student)
            )
            if relationships or old_reports:
                self.stdout.write(
                    f"{legacy_email} -> {canonical_email}: "
                    f"{len(relationships)} parent relationship(s), "
                    f"{len(old_reports)} AI report(s)"
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
                        # Keep the canonical authorization edge and remove only
                        # the obsolete duplicate edge.
                        relationship.delete()
                    else:
                        relationship.student = canonical_student
                        relationship.save(update_fields=["student"])
                    changed_relationships += 1

                # Move legacy AI reports only when the canonical student does not
                # already have that exact academic-year/term report. If a
                # canonical report exists, it wins and the historical legacy
                # report remains untouched rather than being overwritten.
                for report in old_reports:
                    conflict = AINarrativeReport.objects.filter(
                        student=canonical_student,
                        academic_year=report.academic_year,
                        term=report.term,
                    ).exclude(pk=report.pk).exists()
                    if conflict:
                        self.stdout.write(
                            self.style.WARNING(
                                "  Report conflict: canonical report already exists "
                                f"for {report.academic_year} / Term {report.term.term_number}; "
                                "legacy report left untouched."
                            )
                        )
                    else:
                        report.student = canonical_student
                        report.save(update_fields=["student"])
                        migrated_reports += 1

                legacy_student.is_active = False
                legacy_student.save(update_fields=["is_active"])
                legacy_user.is_active = False
                legacy_user.save(update_fields=["is_active"])
                deactivated_students += 1

        # The original demo also used parent@keydemo.test. Reconcile that
        # identity using the same explicit email mapping so the parent login and
        # its authorization edges remain attached to the canonical demo graph.
        legacy_parent_user = User.objects.filter(
            email__iexact=self.LEGACY_PARENT_EMAIL
        ).first()
        canonical_parent_user = User.objects.filter(
            email__iexact=self.CANONICAL_PARENT_EMAIL
        ).first()
        if legacy_parent_user:
            legacy_parent = Parent.objects.filter(user=legacy_parent_user).first()
            if legacy_parent:
                if canonical_parent_user is None:
                    if not apply_changes:
                        self.stdout.write(
                            f"{self.LEGACY_PARENT_EMAIL} -> {self.CANONICAL_PARENT_EMAIL}: "
                            "parent account can be renamed in place."
                        )
                    else:
                        legacy_parent_user.email = self.CANONICAL_PARENT_EMAIL
                        legacy_parent_user.is_active = True
                        legacy_parent_user.save(update_fields=["email", "is_active"])
                        self.stdout.write(
                            f"Reused legacy parent account as {self.CANONICAL_PARENT_EMAIL}."
                        )
                else:
                    canonical_parent = Parent.objects.filter(
                        user=canonical_parent_user
                    ).first()
                    if canonical_parent:
                        parent_relationships = list(
                            ParentStudentRelationship.objects.filter(parent=legacy_parent)
                        )
                        self.stdout.write(
                            f"{self.LEGACY_PARENT_EMAIL} -> {self.CANONICAL_PARENT_EMAIL}: "
                            f"{len(parent_relationships)} parent relationship(s)"
                        )
                        if apply_changes:
                            with transaction.atomic():
                                for relationship in parent_relationships:
                                    duplicate = ParentStudentRelationship.objects.filter(
                                        parent=canonical_parent,
                                        student=relationship.student,
                                    ).exclude(pk=relationship.pk).first()
                                    if duplicate:
                                        relationship.delete()
                                    else:
                                        relationship.parent = canonical_parent
                                        relationship.save(update_fields=["parent"])
                                    changed_relationships += 1
                                legacy_parent.is_active = False
                                legacy_parent.save(update_fields=["is_active"])
                                legacy_parent_user.is_active = False
                                legacy_parent_user.save(update_fields=["is_active"])
                                deactivated_parents += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"SKIP {self.LEGACY_PARENT_EMAIL}: canonical user exists but has no Parent profile."
                            )
                        )

        if apply_changes:
            self.stdout.write(
                self.style.SUCCESS(
                    "Reconciliation complete: "
                    f"{changed_relationships} relationship(s) processed; "
                    f"{migrated_reports} AI report(s) migrated; "
                    f"{deactivated_students} legacy student account(s) deactivated; "
                    f"{deactivated_parents} legacy parent account(s) deactivated; "
                    f"{skipped} student mapping(s) skipped."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run only. Re-run with --apply to reconcile the reported identities, "
                    "relationships and eligible AI reports."
                )
            )

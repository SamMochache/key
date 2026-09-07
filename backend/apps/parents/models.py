from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schools.models import School
from apps.students.models import Student
from core.models import BaseModel


class Parent(BaseModel):
    """School-scoped parent/guardian profile linked to a login identity."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="parent_profile",
    )
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name="parents",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "parents"
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return self.user.full_name


class ParentStudentRelationship(BaseModel):
    """Explicit authorization edge between a parent and a student."""

    class Relationship(models.TextChoices):
        PARENT = "PARENT", _("Parent")
        GUARDIAN = "GUARDIAN", _("Guardian")
        SPONSOR = "SPONSOR", _("Sponsor")
        OTHER = "OTHER", _("Other")

    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name="student_relationships",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="parent_relationships",
    )
    relationship = models.CharField(
        max_length=20,
        choices=Relationship.choices,
        default=Relationship.PARENT,
    )
    can_view_reports = models.BooleanField(default=True)
    is_primary_contact = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "parent_student_relationships"
        ordering = ["student__admission_number", "parent__user__last_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "student"],
                name="unique_parent_student_relationship",
            )
        ]

    def __str__(self):
        return f"{self.parent} → {self.student}"

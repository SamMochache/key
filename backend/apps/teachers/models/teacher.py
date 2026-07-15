from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.identity.models import User
from apps.schools.models import School
from core.constants.teacher import (
    EmploymentType,
    TeacherStatus,
)
from core.models import BaseModel
from .department import Department


class Teacher(BaseModel):
    """
    Represents a teacher employed by a school.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="teacher_profile",
    )

    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name="teachers",
    )

    employee_number = models.CharField(
        _("Employee Number"),
        max_length=30,
    )

    employment_type = models.CharField(
        _("Employment Type"),
        max_length=20,
        choices=EmploymentType.choices,
    )

    employment_date = models.DateField()

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=TeacherStatus.choices,
        default=TeacherStatus.ACTIVE,
    )

    department = models.ForeignKey(
    Department,
    on_delete=models.PROTECT,
    related_name="teachers",
)

    class Meta:
        db_table = "teachers"

        constraints = [
            models.UniqueConstraint(
                fields=["school", "employee_number"],
                name="unique_teacher_employee_number",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.first_name} "
            f"{self.user.last_name}"
        )
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import AcademicYear, Classroom, Term
from apps.students.models import Student
from core.constants.enrollment import EnrollmentStatus
from core.models import BaseModel


class Enrollment(BaseModel):
    """
    Represents a student's enrollment into a classroom
    for a specific academic year and term.
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    enrollment_date = models.DateField(
        _("Enrollment Date"),
    )

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ENROLLED,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "enrollments"

        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")

        ordering = [
            "-academic_year",
            "student",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "academic_year",
                    "term",
                ],
                name="unique_student_enrollment_per_term",
            )
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.classroom}"
        )
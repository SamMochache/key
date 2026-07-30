from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.enrollment.models import Enrollment
from apps.identity.models import User
from apps.schools.models import School
from core.models import BaseModel
from .teacher import Teacher


class TeacherObservation(BaseModel):
    """
    Records a teacher's observation of a student's behavior, skills, or performance.
    """

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="observations",
    )

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT,
        related_name="teacher_observations",
    )

    observer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="observations_made",
        help_text=_("The user who recorded this observation (typically the teacher)"),
    )

    title = models.CharField(
        _("Observation Title"),
        max_length=255,
    )

    description = models.TextField(
        _("Observation Description"),
        blank=True,
    )

    observation_date = models.DateField(
        _("Observation Date"),
    )

    observed_at = models.DateTimeField(
        _("Observed At"),
        auto_now_add=True,
    )

    is_shared_with_family = models.BooleanField(
        _("Shared with Family"),
        default=False,
    )

    class Meta:
        db_table = "teacher_observations"
        verbose_name = _("Teacher Observation")
        verbose_name_plural = _("Teacher Observations")
        ordering = ["-observed_at"]

    def __str__(self):
        return f"{self.title} - {self.enrollment.student}"
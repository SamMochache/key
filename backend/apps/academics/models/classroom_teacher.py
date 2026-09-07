from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from .classroom import Classroom


class ClassroomTeacherAssignment(BaseModel):
    """Assigns a teacher to a classroom without limiting the class to one teacher."""

    class Role(models.TextChoices):
        PRIMARY = "PRIMARY", _("Class Teacher")
        ASSISTANT = "ASSISTANT", _("Assistant Teacher")

    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="teacher_assignments")
    teacher = models.ForeignKey("teachers.Teacher", on_delete=models.PROTECT, related_name="classroom_assignments")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PRIMARY)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "classroom_teacher_assignments"
        verbose_name = _("Classroom Teacher Assignment")
        verbose_name_plural = _("Classroom Teacher Assignments")
        constraints = [models.UniqueConstraint(fields=["classroom", "teacher", "role"], name="unique_classroom_teacher_role")]

    def __str__(self):
        return f"{self.classroom} — {self.teacher} ({self.get_role_display()})"

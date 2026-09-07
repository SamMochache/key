from django.db import models

from apps.academics.models import Classroom, Subject, Term
from apps.identity.models import User
from apps.schools.models import BaseModel


class LessonSession(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="lesson_sessions")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="lesson_sessions")
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, related_name="lesson_sessions_taught")
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="lesson_sessions")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    lesson_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-lesson_date", "-start_time"]
        indexes = [
            models.Index(fields=["classroom", "lesson_date"]),
            models.Index(fields=["teacher", "lesson_date"]),
            models.Index(fields=["term", "lesson_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.classroom.name} - {self.lesson_date}"

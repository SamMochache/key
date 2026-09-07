from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel

from .academic_year import AcademicYear
from .term import Term
from apps.schools.models import School


class CalendarEvent(BaseModel):
    class EventType(models.TextChoices):
        ACADEMIC = "ACADEMIC", "Academic"
        HOLIDAY = "HOLIDAY", "Holiday"
        EXAMINATION = "EXAMINATION", "Examination"
        MEETING = "MEETING", "Meeting"
        ACTIVITY = "ACTIVITY", "Activity"
        DEADLINE = "DEADLINE", "Deadline"
        OTHER = "OTHER", "Other"

    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="calendar_events")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="calendar_events")
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="calendar_events", null=True, blank=True)
    title = models.CharField(max_length=160)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.ACADEMIC)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "calendar_events"
        ordering = ["start_at", "title"]
        indexes = [
            models.Index(fields=["school", "start_at"]),
            models.Index(fields=["school", "academic_year", "term"]),
        ]

    def clean(self):
        if self.end_at < self.start_at:
            raise ValidationError({"end_at": "End time cannot be before start time."})
        if self.academic_year_id and self.school_id and self.academic_year.school_id != self.school_id:
            raise ValidationError({"academic_year": "Academic year must belong to the selected institution."})
        if self.term_id:
            if self.term.academic_year_id != self.academic_year_id:
                raise ValidationError({"term": "Term must belong to the selected academic year."})
            if self.term.academic_year.school_id != self.school_id:
                raise ValidationError({"term": "Term must belong to the selected institution."})

    def __str__(self):
        return self.title

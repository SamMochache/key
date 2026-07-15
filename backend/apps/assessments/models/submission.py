from django.conf import settings
from django.db import models 
from django.utils.translation import gettext_lazy as _ 
from apps.enrollment.models import Enrollment 
from core.constants.assessment import SubmissionStatus 
from core.models import BaseModel 
from .assessment import Assessment 

class AssessmentSubmission(BaseModel): 
    """ Represents a student's submission for an assessment. """ 
    assessment = models.ForeignKey( Assessment, on_delete=models.CASCADE, related_name="submissions", ) 
    enrollment = models.ForeignKey( Enrollment, on_delete=models.PROTECT, related_name="assessment_submissions", ) 
    submitted_at = models.DateTimeField( null=True, blank=True, ) 
    submission_text = models.TextField( blank=True, ) 
    submission_file = models.FileField( upload_to="assessments/submissions/", blank=True, null=True, ) 
    submission_url = models.URLField( blank=True, ) 
    status = models.CharField( max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.DRAFT, ) 
    is_late = models.BooleanField( default=False, ) 
    teacher_notes = models.TextField( blank=True, ) 

    submitted_by = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assessment_submissions", )
    
    class Meta: 
        db_table = "assessment_submissions" 
        ordering = [ "-submitted_at", ] 
        constraints = [ models.UniqueConstraint( fields=[ "assessment", "enrollment", ], 
        name="unique_student_assessment_submission", ) ] 
        def __str__(self): 
            return ( f"{self.enrollment.student} - " f"{self.assessment.title}" )
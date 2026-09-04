from django.db import models 
from django.utils.translation import gettext_lazy as _ 
from core.models import BaseModel 
from .assessment import Assessment 

class Rubric(BaseModel): 
    """ Grading rubric attached to an assessment. """ 
    assessment = models.OneToOneField( Assessment, on_delete=models.CASCADE, related_name="rubric", ) 
    title = models.CharField( _("Rubric Title"), max_length=255, ) 
    description = models.TextField( blank=True, ) 
    
    class Meta: db_table = "assessment_rubrics" 
    verbose_name = _("Assessment Rubric") 
    verbose_name_plural = _("Assessment Rubrics") 
    def __str__(self): 
        return self.title
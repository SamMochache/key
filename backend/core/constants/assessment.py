from django.db import models
from django.utils.translation import gettext_lazy as _


class AssessmentType(models.TextChoices):
    """
    Types of academic assessments.
    """

    ASSIGNMENT = "ASSIGNMENT", _("Assignment")
    QUIZ = "QUIZ", _("Quiz")
    PROJECT = "PROJECT", _("Project")
    PRACTICAL = "PRACTICAL", _("Practical Activity")
    PRESENTATION = "PRESENTATION", _("Presentation")
    OBSERVATION = "OBSERVATION", _("Teacher Observation")
    HOMEWORK = "HOMEWORK", _("Homework")
    PORTFOLIO = "PORTFOLIO", _("Portfolio Review")

class AssessmentStatus(models.TextChoices):
    """
    Workflow state of an assessment.
    """

    DRAFT = "DRAFT", _("Draft")
    PUBLISHED = "PUBLISHED", _("Published")
    CLOSED = "CLOSED", _("Closed")

class SubmissionStatus(models.TextChoices): 
    """ Workflow state of an assessment submission. """
    DRAFT = "DRAFT", _("Draft") 
    SUBMITTED = "SUBMITTED", _("Submitted") 
    RETURNED = "RETURNED", _("Returned") 
    GRADED = "GRADED", _("Graded")
from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.students.models import Student

from .models import Assessment, AssessmentEvaluation, AssessmentSubmission, CompetencyEvaluation, CriterionScore, Rubric, RubricCriterion
from .serializers import (
    AssessmentEvaluationSerializer,
    AssessmentSerializer,
    AssessmentSubmissionSerializer,
    CompetencyEvaluationSerializer,
    CriterionScoreSerializer,
    RubricCriterionSerializer,
    RubricSerializer,
)


class SchoolScopedQuerysetMixin:
    def school_for_user(self):
        user = self.request.user
        if user.is_superuser:
            return None
        try:
            return user.teacher_profile.school
        except AttributeError:
            pass
        try:
            return user.student_profile.school
        except AttributeError:
            return None

    def filter_school(self, queryset, school_field):
        school = self.school_for_user()
        if school is None:
            return queryset
        return queryset.filter(**{school_field: school})


class AssessmentViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Assessment.objects.select_related("teacher__user", "lesson_session").prefetch_related("rubric__criteria")
        return self.filter_school(queryset, "teacher__school")


class AssessmentSubmissionViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AssessmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = AssessmentSubmission.objects.select_related(
            "assessment", "enrollment__student__user", "submitted_by"
        )
        return self.filter_school(queryset, "enrollment__student__school")

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class RubricViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = RubricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Rubric.objects.select_related("assessment__teacher__school").prefetch_related("criteria")
        return self.filter_school(queryset, "assessment__teacher__school")


class RubricCriterionViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = RubricCriterionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RubricCriterion.objects.select_related("rubric__assessment__teacher__school")
        return self.filter_school(queryset, "rubric__assessment__teacher__school")


class AssessmentEvaluationViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AssessmentEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = AssessmentEvaluation.objects.select_related(
            "submission__assessment__teacher__school",
            "submission__enrollment__student__user",
        ).prefetch_related("criterion_scores", "competency_evaluations__competency")
        return self.filter_school(queryset, "submission__enrollment__student__school")

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        evaluation = self.get_object()
        evaluation.published = True
        evaluation.published_at = timezone.now()
        evaluation.save(update_fields=["published", "published_at", "updated_at"])
        return Response(self.get_serializer(evaluation).data)


class CriterionScoreViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CriterionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CriterionScore.objects.select_related(
            "evaluation__submission__enrollment__student__school"
        )
        return self.filter_school(queryset, "evaluation__submission__enrollment__student__school")


class CompetencyEvaluationViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CompetencyEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CompetencyEvaluation.objects.select_related(
            "evaluation__submission__enrollment__student__school", "competency"
        )
        return self.filter_school(queryset, "evaluation__submission__enrollment__student__school")


class DashboardSummaryView(SchoolScopedQuerysetMixin, viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        school = self.school_for_user()
        students = Student.objects.filter(is_active=True)
        assessments = Assessment.objects.all()
        submissions = AssessmentSubmission.objects.all()
        evaluations = AssessmentEvaluation.objects.all()

        if school is not None:
            students = students.filter(school=school)
            assessments = assessments.filter(teacher__school=school)
            submissions = submissions.filter(enrollment__student__school=school)
            evaluations = evaluations.filter(submission__enrollment__student__school=school)

        return Response({
            "students": students.count(),
            "assessments": assessments.count(),
            "submissions": submissions.count(),
            "evaluations": evaluations.count(),
            "published_evaluations": evaluations.filter(published=True).count(),
            "upcoming_assessments": assessments.filter(due_date__gte=timezone.localdate()).count(),
        })

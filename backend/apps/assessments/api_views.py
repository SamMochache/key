from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.students.models import Student

from core.constants.assessment import SubmissionStatus

from .models import (
    Assessment,
    AssessmentEvaluation,
    AssessmentSubmission,
    CompetencyEvaluation,
    CriterionScore,
    Rubric,
    RubricCriterion,
)
from .permissions import (
    AssessmentAccessPermission,
    EvaluationAccessPermission,
    SubmissionAccessPermission,
    TeacherOrAdmin,
    UserRole,
    get_user_role,
    get_user_school,
)
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
        return get_user_school(self.request.user)

    def filter_school(self, queryset, school_field):
        role = get_user_role(self.request.user)
        if role == UserRole.ADMIN:
            return queryset

        school = self.school_for_user()
        if school is None:
            raise PermissionDenied("Your account is not associated with an institution.")
        return queryset.filter(**{school_field: school})


class AssessmentViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [AssessmentAccessPermission]

    def get_queryset(self):
        queryset = Assessment.objects.select_related(
            "teacher__user", "teacher__school", "lesson_session"
        ).prefetch_related("rubric__criteria")
        return self.filter_school(queryset, "teacher__school")

    def perform_create(self, serializer):
        if get_user_role(self.request.user) == UserRole.ADMIN:
            serializer.save()
            return
        try:
            teacher = self.request.user.teacher_profile
        except ObjectDoesNotExist as exc:
            raise PermissionDenied("Only teachers can create assessments.") from exc
        serializer.save(teacher=teacher)


class AssessmentSubmissionViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AssessmentSubmissionSerializer
    permission_classes = [SubmissionAccessPermission]

    def get_queryset(self):
        queryset = AssessmentSubmission.objects.select_related(
            "assessment__teacher__school",
            "assessment",
            "enrollment__student__user",
            "enrollment__student__school",
            "submitted_by",
        )
        role = get_user_role(self.request.user)
        if role == UserRole.STUDENT:
            return queryset.filter(enrollment__student__user=self.request.user)
        return self.filter_school(queryset, "enrollment__student__school")

    def perform_create(self, serializer):
        role = get_user_role(self.request.user)
        if role == UserRole.STUDENT:
            try:
                student = self.request.user.student_profile
            except ObjectDoesNotExist as exc:
                raise PermissionDenied("Student profile not found.") from exc
            enrollment = serializer.validated_data.get("enrollment")
            if enrollment is None or enrollment.student_id != student.id:
                raise PermissionDenied("You can only submit work for your own enrollment.")
        serializer.save(submitted_by=self.request.user)

    def perform_update(self, serializer):
        if get_user_role(self.request.user) == UserRole.STUDENT:
            submission = self.get_object()
            if submission.enrollment.student.user_id != self.request.user.id:
                raise PermissionDenied("You can only edit your own submission.")
            if submission.status == SubmissionStatus.GRADED:
                raise PermissionDenied("A graded submission cannot be edited.")
        serializer.save()


class RubricViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = RubricSerializer
    permission_classes = [TeacherOrAdmin]

    def get_queryset(self):
        queryset = Rubric.objects.select_related(
            "assessment__teacher__school"
        ).prefetch_related("criteria")
        return self.filter_school(queryset, "assessment__teacher__school")


class RubricCriterionViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = RubricCriterionSerializer
    permission_classes = [TeacherOrAdmin]

    def get_queryset(self):
        queryset = RubricCriterion.objects.select_related(
            "rubric__assessment__teacher__school"
        )
        return self.filter_school(queryset, "rubric__assessment__teacher__school")


class AssessmentEvaluationViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AssessmentEvaluationSerializer
    permission_classes = [EvaluationAccessPermission]

    def get_queryset(self):
        queryset = AssessmentEvaluation.objects.select_related(
            "submission__assessment__teacher__school",
            "submission__enrollment__student__user",
        ).prefetch_related("criterion_scores", "competency_evaluations__competency")
        return self.filter_school(queryset, "submission__enrollment__student__school")

    def perform_create(self, serializer):
        evaluation = serializer.save()
        self._recalculate(evaluation)

    def perform_update(self, serializer):
        evaluation = serializer.save()
        self._recalculate(evaluation)

    @transaction.atomic
    def _recalculate(self, evaluation):
        total = evaluation.criterion_scores.aggregate(total=Sum("score"))["total"] or 0
        maximum = evaluation.submission.assessment.maximum_score
        if maximum is None:
            maximum = evaluation.submission.assessment.rubric.criteria.aggregate(
                total=Sum("maximum_score")
            )["total"] or 0

        evaluation.total_score = total
        evaluation.percentage = (total / maximum * 100) if maximum else None
        evaluation.save(update_fields=["total_score", "percentage", "updated_at"])

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        evaluation = self.get_object()
        if not evaluation.criterion_scores.exists():
            return Response(
                {"detail": "An evaluation must have at least one criterion score before publishing."},
                status=400,
            )

        self._recalculate(evaluation)
        evaluation.published = True
        evaluation.published_at = timezone.now()
        evaluation.submission.status = SubmissionStatus.GRADED
        evaluation.submission.save(update_fields=["status", "updated_at"])
        evaluation.save(update_fields=["published", "published_at", "updated_at"])
        return Response(self.get_serializer(evaluation).data)


class CriterionScoreViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CriterionScoreSerializer
    permission_classes = [EvaluationAccessPermission]

    def get_queryset(self):
        queryset = CriterionScore.objects.select_related(
            "criterion",
            "evaluation__submission__assessment__teacher__school",
            "evaluation__submission__enrollment__student__school",
        )
        return self.filter_school(queryset, "evaluation__submission__enrollment__student__school")

    def _validate_score(self, score, criterion):
        if score is not None and score < 0:
            raise PermissionDenied("Score cannot be negative.")
        if score is not None and criterion is not None and score > criterion.maximum_score:
            raise PermissionDenied("Score cannot exceed the criterion maximum.")

    def perform_create(self, serializer):
        self._validate_score(
            serializer.validated_data.get("score"),
            serializer.validated_data.get("criterion"),
        )
        serializer.save()
        self._recalculate(serializer.instance.evaluation)

    def perform_update(self, serializer):
        self._validate_score(
            serializer.validated_data.get("score", serializer.instance.score),
            serializer.validated_data.get("criterion", serializer.instance.criterion),
        )
        serializer.save()
        self._recalculate(serializer.instance.evaluation)

    @staticmethod
    def _recalculate(evaluation):
        total = evaluation.criterion_scores.aggregate(total=Sum("score"))["total"] or 0
        maximum = evaluation.submission.assessment.maximum_score
        if maximum is None:
            maximum = evaluation.submission.assessment.rubric.criteria.aggregate(
                total=Sum("maximum_score")
            )["total"] or 0
        evaluation.total_score = total
        evaluation.percentage = (total / maximum * 100) if maximum else None
        evaluation.save(update_fields=["total_score", "percentage", "updated_at"])


class CompetencyEvaluationViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CompetencyEvaluationSerializer
    permission_classes = [EvaluationAccessPermission]

    def get_queryset(self):
        queryset = CompetencyEvaluation.objects.select_related(
            "competency",
            "evaluation__submission__assessment__teacher__school",
            "evaluation__submission__enrollment__student__school",
        )
        return self.filter_school(queryset, "evaluation__submission__enrollment__student__school")


class DashboardSummaryView(SchoolScopedQuerysetMixin, viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        school = self.school_for_user()
        role = get_user_role(request.user)

        if role not in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT}:
            raise PermissionDenied("Your account does not have dashboard access.")

        students = Student.objects.filter(is_active=True)
        assessments = Assessment.objects.all()
        submissions = AssessmentSubmission.objects.all()
        evaluations = AssessmentEvaluation.objects.all()

        if role == UserRole.STUDENT:
            students = students.filter(user=request.user)
            submissions = submissions.filter(enrollment__student__user=request.user)
            evaluations = evaluations.filter(submission__enrollment__student__user=request.user)
            assessments = assessments.filter(teacher__school=school)
        elif school is not None:
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

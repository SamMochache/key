from rest_framework import serializers

from .models import (
    Assessment,
    AssessmentEvaluation,
    AssessmentSubmission,
    CompetencyEvaluation,
    CriterionScore,
    Rubric,
    RubricCriterion,
)


class RubricCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricCriterion
        fields = ["id", "title", "description", "maximum_score", "sequence"]


class RubricSerializer(serializers.ModelSerializer):
    criteria = RubricCriterionSerializer(many=True, read_only=True)

    class Meta:
        model = Rubric
        fields = ["id", "title", "description", "criteria"]


class AssessmentSerializer(serializers.ModelSerializer):
    rubric = RubricSerializer(read_only=True)
    teacher_name = serializers.CharField(source="teacher.user.full_name", read_only=True)
    lesson_session_title = serializers.SerializerMethodField()

    def get_lesson_session_title(self, obj):
        return str(obj.lesson_session)

    class Meta:
        model = Assessment
        fields = [
            "id", "lesson_session", "lesson_session_title", "teacher", "teacher_name",
            "title", "description", "assessment_type", "status", "due_date",
            "maximum_score", "allow_resubmission", "rubric", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class AssessmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="enrollment.student.user.full_name", read_only=True)
    admission_number = serializers.CharField(source="enrollment.student.admission_number", read_only=True)

    class Meta:
        model = AssessmentSubmission
        fields = [
            "id", "assessment", "enrollment", "student_name", "admission_number",
            "submitted_at", "submission_text", "submission_file", "submission_url",
            "status", "is_late", "teacher_notes", "submitted_by", "created_at", "updated_at",
        ]
        read_only_fields = ["submitted_by", "created_at", "updated_at", "is_late"]


class CriterionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CriterionScore
        fields = ["id", "evaluation", "criterion", "score", "feedback", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class CompetencyEvaluationSerializer(serializers.ModelSerializer):
    competency_name = serializers.CharField(source="competency.name", read_only=True)

    class Meta:
        model = CompetencyEvaluation
        fields = [
            "id", "evaluation", "competency", "competency_name", "level",
            "teacher_comment", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class AssessmentEvaluationSerializer(serializers.ModelSerializer):
    criterion_scores = CriterionScoreSerializer(many=True, read_only=True)
    competency_evaluations = CompetencyEvaluationSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="submission.enrollment.student.user.full_name", read_only=True)

    class Meta:
        model = AssessmentEvaluation
        fields = [
            "id", "submission", "student_name", "total_score", "percentage",
            "narrative_feedback", "published", "published_at", "criterion_scores",
            "competency_evaluations", "created_at", "updated_at",
        ]
        read_only_fields = ["total_score", "percentage", "published_at", "created_at", "updated_at"]

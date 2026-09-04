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
from .permissions import UserRole, get_user_role, get_user_school


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

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = get_user_role(user)

        teacher = attrs.get("teacher", getattr(self.instance, "teacher", None))
        if role == UserRole.TEACHER:
            current_teacher = getattr(user, "teacher_profile", None)
            if teacher is not None and current_teacher is not None and teacher != current_teacher:
                raise serializers.ValidationError({"teacher": "Teachers can only manage their own assessments."})

        return attrs

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

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = get_user_role(user)

        assessment = attrs.get("assessment", getattr(self.instance, "assessment", None))
        enrollment = attrs.get("enrollment", getattr(self.instance, "enrollment", None))

        if assessment is not None and enrollment is not None:
            assessment_school_id = assessment.teacher.school_id
            enrollment_school_id = enrollment.student.school_id
            if assessment_school_id != enrollment_school_id:
                raise serializers.ValidationError(
                    "The assessment and enrollment must belong to the same institution."
                )

        if role == UserRole.STUDENT:
            student = getattr(user, "student_profile", None)
            if student is None:
                raise serializers.ValidationError("Student profile not found.")
            if enrollment is not None and enrollment.student_id != student.id:
                raise serializers.ValidationError({"enrollment": "You can only use your own enrollment."})
            if assessment is not None and assessment.status != "PUBLISHED":
                raise serializers.ValidationError({"assessment": "Only published assessments accept submissions."})

        return attrs

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if get_user_role(user) == UserRole.STUDENT:
            extra_kwargs.update({
                "status": {"read_only": True},
                "teacher_notes": {"read_only": True},
            })
        return extra_kwargs

    class Meta:
        model = AssessmentSubmission
        fields = [
            "id", "assessment", "enrollment", "student_name", "admission_number",
            "submitted_at", "submission_text", "submission_file", "submission_url",
            "status", "is_late", "teacher_notes", "submitted_by", "created_at", "updated_at",
        ]
        read_only_fields = ["submitted_by", "created_at", "updated_at", "is_late"]


class CriterionScoreSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        evaluation = attrs.get("evaluation", getattr(self.instance, "evaluation", None))
        criterion = attrs.get("criterion", getattr(self.instance, "criterion", None))
        score = attrs.get("score", getattr(self.instance, "score", None))

        if evaluation is not None and criterion is not None:
            assessment = evaluation.submission.assessment
            if not hasattr(assessment, "rubric") or criterion.rubric_id != assessment.rubric_id:
                raise serializers.ValidationError(
                    {"criterion": "The criterion must belong to the assessment rubric."}
                )

        if score is not None and score < 0:
            raise serializers.ValidationError({"score": "Score cannot be negative."})
        if score is not None and criterion is not None and score > criterion.maximum_score:
            raise serializers.ValidationError({"score": "Score cannot exceed the criterion maximum."})

        request = self.context.get("request")
        user = getattr(request, "user", None)
        school = get_user_school(user)
        if school is not None and evaluation is not None:
            submission_school_id = evaluation.submission.enrollment.student.school_id
            if submission_school_id != school.id:
                raise serializers.ValidationError("You cannot score a submission from another institution.")

        return attrs

    class Meta:
        model = CriterionScore
        fields = ["id", "evaluation", "criterion", "score", "feedback", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class CompetencyEvaluationSerializer(serializers.ModelSerializer):
    competency_name = serializers.CharField(source="competency.name", read_only=True)

    def validate(self, attrs):
        evaluation = attrs.get("evaluation", getattr(self.instance, "evaluation", None))
        request = self.context.get("request")
        user = getattr(request, "user", None)
        school = get_user_school(user)
        if school is not None and evaluation is not None:
            submission_school_id = evaluation.submission.enrollment.student.school_id
            if submission_school_id != school.id:
                raise serializers.ValidationError(
                    "You cannot evaluate a submission from another institution."
                )
        return attrs

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

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = get_user_role(user)
        submission = attrs.get("submission", getattr(self.instance, "submission", None))
        if submission is None:
            return attrs

        if self.instance is not None and submission != self.instance.submission:
            raise serializers.ValidationError({"submission": "An evaluation cannot be moved to another submission."})

        school = get_user_school(user)
        if school is not None and submission.enrollment.student.school_id != school.id:
            raise serializers.ValidationError(
                {"submission": "You cannot evaluate a submission from another institution."}
            )

        if role == UserRole.TEACHER:
            teacher = getattr(user, "teacher_profile", None)
            if teacher is not None and submission.assessment.teacher_id != teacher.id:
                raise serializers.ValidationError(
                    {"submission": "Teachers can only evaluate assessments assigned to them."}
                )

        return attrs

    class Meta:
        model = AssessmentEvaluation
        fields = [
            "id", "submission", "student_name", "total_score", "percentage",
            "narrative_feedback", "published", "published_at", "criterion_scores",
            "competency_evaluations", "created_at", "updated_at",
        ]
        read_only_fields = [
            "total_score", "percentage", "published", "published_at",
            "created_at", "updated_at",
        ]

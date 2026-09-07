from rest_framework import serializers

from .models import Evidence
from .permissions import UserRole, get_user_role, get_user_school


class EvidenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source="submission.enrollment.student.user.full_name",
        read_only=True,
    )
    assessment_title = serializers.CharField(
        source="submission.assessment.title",
        read_only=True,
    )
    competency_name = serializers.CharField(
        source="competency.name",
        read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = get_user_role(user)
        submission = attrs.get("submission", getattr(self.instance, "submission", None))
        competency = attrs.get("competency", getattr(self.instance, "competency", None))

        if submission is None:
            return attrs

        school_id = submission.enrollment.student.school_id
        school = get_user_school(user)
        if school is not None and school_id != school.id:
            raise serializers.ValidationError(
                "You cannot manage evidence from another institution."
            )

        if competency is not None and competency.school_id != school_id:
            raise serializers.ValidationError(
                {"competency": "The competency must belong to the same institution."}
            )

        if role == UserRole.TEACHER:
            teacher = getattr(user, "teacher_profile", None)
            if teacher is None or submission.assessment.teacher_id != teacher.id:
                raise serializers.ValidationError(
                    "Teachers can only manage evidence for their own assessments."
                )

        if not attrs.get("file") and not attrs.get("url") and not attrs.get("description"):
            raise serializers.ValidationError(
                "Evidence must contain a file, URL, or description."
            )

        return attrs

    class Meta:
        model = Evidence
        fields = [
            "id",
            "submission",
            "student_name",
            "assessment_title",
            "competency",
            "competency_name",
            "title",
            "description",
            "evidence_type",
            "file",
            "file_url",
            "url",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
            "student_name",
            "assessment_title",
            "competency_name",
            "created_by_name",
            "file_url",
        ]

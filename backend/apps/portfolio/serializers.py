from rest_framework import serializers

from .models import Artifact, Portfolio, PortfolioItem


class ArtifactSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url

    class Meta:
        model = Artifact
        fields = ["id", "portfolio_item", "file", "file_url", "caption", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at", "file_url"]


class PortfolioItemSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="portfolio.student.user.full_name", read_only=True)
    artifacts = ArtifactSerializer(many=True, read_only=True)
    item_type_label = serializers.CharField(source="get_item_type_display", read_only=True)
    assessment_title = serializers.CharField(source="assessment_submission.assessment.title", read_only=True)

    class Meta:
        model = PortfolioItem
        fields = [
            "id", "portfolio", "student_name", "lesson_session", "assessment_submission",
            "assessment_title", "item_type", "item_type_label", "title", "description",
            "event_date", "artifacts", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "student_name", "assessment_title", "artifacts", "item_type_label"]

    def validate(self, attrs):
        portfolio = attrs.get("portfolio", getattr(self.instance, "portfolio", None))
        if portfolio is None:
            raise serializers.ValidationError({"portfolio": "A portfolio is required."})
        submission = attrs.get("assessment_submission", getattr(self.instance, "assessment_submission", None))
        lesson = attrs.get("lesson_session", getattr(self.instance, "lesson_session", None))
        if submission and submission.enrollment.student_id != portfolio.student_id:
            raise serializers.ValidationError({"assessment_submission": "The submission must belong to this student."})
        if lesson and not lesson.timetable_entry.classroom.enrollments.filter(student_id=portfolio.student_id).exists():
            raise serializers.ValidationError({"lesson_session": "The lesson must belong to this student's class."})
        return attrs


class PortfolioSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    item_count = serializers.SerializerMethodField()

    def get_item_count(self, obj):
        return obj.items.count()

    def validate_student(self, student):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = getattr(request, "portfolio_role", None)
        student_profile = getattr(user, "student_profile", None)
        if role == "student" and (student_profile is None or student_profile.id != student.id):
            raise serializers.ValidationError("You can only manage your own portfolio.")
        return student

    class Meta:
        model = Portfolio
        fields = ["id", "student", "student_name", "admission_number", "summary", "item_count", "created_at", "updated_at"]
        read_only_fields = ["student_name", "admission_number", "item_count", "created_at", "updated_at"]

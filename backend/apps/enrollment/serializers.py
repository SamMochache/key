from rest_framework import serializers

from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_email = serializers.EmailField(source="student.user.email", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_number = serializers.IntegerField(source="term.term_number", read_only=True)
    school_id = serializers.UUIDField(source="classroom.school_id", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "student_name", "student_email", "admission_number",
            "classroom", "classroom_name", "academic_year", "academic_year_name",
            "term", "term_number", "enrollment_date", "status", "remarks", "school_id",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "student_name", "student_email", "admission_number", "classroom_name",
            "academic_year_name", "term_number", "school_id", "created_at", "updated_at",
        ]

    def validate(self, attrs):
        student = attrs.get("student", getattr(self.instance, "student", None))
        classroom = attrs.get("classroom", getattr(self.instance, "classroom", None))
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        term = attrs.get("term", getattr(self.instance, "term", None))

        if not all([student, classroom, academic_year, term]):
            return attrs

        if student.school_id != classroom.school_id:
            raise serializers.ValidationError({"student": "Student and classroom must belong to the same institution."})
        if academic_year.school_id != classroom.school_id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to the classroom institution."})
        if term.academic_year_id != academic_year.id:
            raise serializers.ValidationError({"term": "Term must belong to the selected academic year."})
        if classroom.academic_year_id != academic_year.id:
            raise serializers.ValidationError({"classroom": "Classroom must belong to the selected academic year."})
        if classroom.term_id != term.id:
            raise serializers.ValidationError({"classroom": "Classroom must belong to the selected term."})

        duplicate = Enrollment.objects.filter(
            student=student,
            academic_year=academic_year,
            term=term,
        )
        if self.instance is not None:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError({"student": "This student is already enrolled for this academic year and term."})

        return attrs

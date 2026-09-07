from django.db.models import Count
from rest_framework import viewsets

from .models import School
from .permissions import SchoolAccessPermission
from .serializers import SchoolSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    """Institution directory with strict school-level tenant isolation."""

    serializer_class = SchoolSerializer
    permission_classes = [SchoolAccessPermission]

    def get_queryset(self):
        queryset = School.objects.annotate(
            student_count=Count("students", distinct=True),
            teacher_count=Count("teachers", distinct=True),
        )

        user = self.request.user
        if user.is_staff or user.is_superuser:
            return queryset

        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile is not None:
            return queryset.filter(pk=teacher_profile.school_id)

        student_profile = getattr(user, "student_profile", None)
        if student_profile is not None:
            return queryset.filter(pk=student_profile.school_id)

        return queryset.none()

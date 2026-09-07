from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Return the authenticated teacher/student's own institution."""
        user = request.user

        teacher_profile = getattr(user, "teacher_profile", None)
        student_profile = getattr(user, "student_profile", None)
        profile = teacher_profile or student_profile

        if profile is None:
            if user.is_staff or user.is_superuser:
                return Response(
                    {"detail": "Administrators do not have a single institution context."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                {"detail": "Your account is not associated with an institution."},
                status=status.HTTP_403_FORBIDDEN,
            )

        school = self.get_queryset().get(pk=profile.school_id)
        return Response(self.get_serializer(school).data)

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

        for relation in ("teacher_profile", "student_profile", "parent_profile"):
            profile = getattr(user, relation, None)
            if profile is not None:
                return queryset.filter(pk=profile.school_id)
        return queryset.none()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Return the authenticated user's own institution."""
        user = request.user
        if user.is_staff or user.is_superuser:
            return Response(
                {"detail": "Administrators do not have a single institution context."},
                status=status.HTTP_403_FORBIDDEN,
            )

        for relation in ("teacher_profile", "student_profile", "parent_profile"):
            profile = getattr(user, relation, None)
            if profile is not None:
                school = self.get_queryset().get(pk=profile.school_id)
                return Response(self.get_serializer(school).data)

        return Response(
            {"detail": "Your account is not associated with an institution."},
            status=status.HTTP_403_FORBIDDEN,
        )

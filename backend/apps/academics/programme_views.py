from rest_framework import permissions, viewsets

from .models import Programme
from .serializers import ProgrammeSerializer


class ProgrammeAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user.is_staff or request.user.is_superuser or getattr(request.user, "teacher_profile", None) is not None or getattr(request.user, "student_profile", None) is not None)
        return bool(request.user.is_staff or request.user.is_superuser)


class ProgrammeViewSet(viewsets.ModelViewSet):
    serializer_class = ProgrammeSerializer
    permission_classes = [ProgrammeAdminPermission]

    def get_queryset(self):
        queryset = Programme.objects.select_related("curriculum").all()
        curriculum = self.request.query_params.get("curriculum")
        if curriculum:
            queryset = queryset.filter(curriculum_id=curriculum)
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        return queryset

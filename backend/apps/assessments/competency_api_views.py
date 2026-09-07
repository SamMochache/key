from rest_framework import permissions, viewsets

from .models import Competency
from .permissions import UserRole, get_user_role, get_user_school
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers


class CompetencyReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competency
        fields = ["id", "name", "description", "sequence", "is_active"]


class CompetencyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompetencyReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        role = get_user_role(self.request.user)
        if role == UserRole.ADMIN:
            return Competency.objects.all()
        school = get_user_school(self.request.user)
        if school is None:
            raise PermissionDenied("Your account is not associated with an institution.")
        return Competency.objects.filter(school=school, is_active=True)

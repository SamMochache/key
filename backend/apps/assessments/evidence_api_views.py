from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .evidence_serializers import EvidenceSerializer
from .models import Evidence
from .permissions import UserRole, get_user_role, get_user_school


class EvidenceViewSet(viewsets.ModelViewSet):
    serializer_class = EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Evidence.objects.select_related(
            "submission__assessment__teacher__school",
            "submission__enrollment__student__user",
            "submission__enrollment__student__school",
            "competency",
            "created_by",
        )
        role = get_user_role(self.request.user)
        if role == UserRole.ADMIN:
            return queryset

        school = get_user_school(self.request.user)
        if school is None:
            raise PermissionDenied("Your account is not associated with an institution.")

        queryset = queryset.filter(submission__enrollment__student__school=school)
        if role == UserRole.STUDENT:
            return queryset.filter(
                submission__enrollment__student__user=self.request.user
            )
        return queryset

    def perform_create(self, serializer):
        role = get_user_role(self.request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only teachers and administrators can add evidence.")
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        role = get_user_role(self.request.user)
        if role == UserRole.TEACHER:
            try:
                teacher = self.request.user.teacher_profile
            except ObjectDoesNotExist as exc:
                raise PermissionDenied("Teacher profile not found.") from exc
            if serializer.instance.submission.assessment.teacher_id != teacher.id:
                raise PermissionDenied("You can only edit evidence for your own assessments.")
        elif role != UserRole.ADMIN:
            raise PermissionDenied("Only teachers and administrators can edit evidence.")
        serializer.save()

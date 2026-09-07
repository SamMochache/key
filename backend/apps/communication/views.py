from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.schools.models import School

from .models import CommunicationMessage
from .serializers import CommunicationContactSerializer, CommunicationMessageSerializer

User = get_user_model()


def is_admin(user):
    return bool(user.is_staff or user.is_superuser)


def user_school(user):
    for relation in ("teacher_profile", "student_profile", "parent_profile"):
        profile = getattr(user, relation, None)
        if profile is not None:
            return profile.school
    return None


def scoped_users(school):
    return User.objects.filter(
        Q(teacher_profile__school=school)
        | Q(student_profile__school=school)
        | Q(parent_profile__school=school)
    ).filter(is_active=True).distinct()


class CommunicationAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return is_admin(request.user) or user_school(request.user) is not None


class CommunicationMessageViewSet(viewsets.ModelViewSet):
    serializer_class = CommunicationMessageSerializer
    permission_classes = [CommunicationAccessPermission]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = CommunicationMessage.objects.select_related("sender", "recipient", "school")
        school_id = self.request.query_params.get("school")
        school = get_object_or_404(School, pk=school_id) if is_admin(user) and school_id else user_school(user)
        if school is None:
            return qs.none()
        qs = qs.filter(school=school)
        folder = self.request.query_params.get("folder", "inbox")
        if folder == "sent":
            qs = qs.filter(sender=user)
        else:
            qs = qs.filter(recipient=user)
        if self.request.query_params.get("unread") == "true":
            qs = qs.filter(read_at__isnull=True)
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        recipient_id = data.get("recipient")
        if not recipient_id:
            return Response({"recipient": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        school = user_school(request.user)
        if is_admin(request.user) and data.get("school"):
            school = get_object_or_404(School, pk=data["school"])
        if school is None:
            return Response({"detail": "Select an institution before sending a message."}, status=status.HTTP_400_BAD_REQUEST)

        recipient = get_object_or_404(scoped_users(school), pk=recipient_id)
        if recipient == request.user:
            return Response({"recipient": ["You cannot send a message to yourself."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={**data, "school": str(school.pk), "recipient": str(recipient.pk)})
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        message = get_object_or_404(self.get_queryset(), pk=pk)
        if message.recipient_id != request.user.id:
            return Response({"detail": "Only the recipient can mark this message as read."}, status=status.HTTP_403_FORBIDDEN)
        if message.read_at is None:
            message.read_at = timezone.now()
            message.save(update_fields=["read_at", "updated_at"])
        return Response(self.get_serializer(message).data)


class CommunicationContactsView(viewsets.ViewSet):
    permission_classes = [CommunicationAccessPermission]

    def list(self, request):
        school = user_school(request.user)
        if is_admin(request.user) and request.query_params.get("school"):
            school = get_object_or_404(School, pk=request.query_params["school"])
        if school is None:
            return Response([])
        contacts = scoped_users(school).exclude(pk=request.user.pk)
        search = request.query_params.get("search", "").strip()
        if search:
            contacts = contacts.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
        return Response(CommunicationContactSerializer(contacts.order_by("first_name", "last_name"), many=True).data)

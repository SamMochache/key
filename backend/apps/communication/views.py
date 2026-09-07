from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.schools.models import School
from apps.notifications.services import notify
from apps.notifications.models import Notification

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


def scoped_users(school=None):
    qs = User.objects.filter(is_active=True)
    profile_filter = Q(teacher_profile__isnull=False) | Q(student_profile__isnull=False) | Q(parent_profile__isnull=False)
    if school is not None:
        profile_filter &= Q(teacher_profile__school=school) | Q(student_profile__school=school) | Q(parent_profile__school=school)
    return qs.filter(profile_filter).distinct()


def recipient_school(user):
    for relation in ("teacher_profile", "student_profile", "parent_profile"):
        profile = getattr(user, relation, None)
        if profile is not None:
            return profile.school
    return None


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
        if school is not None:
            qs = qs.filter(school=school)
        elif not is_admin(user):
            return qs.none()
        folder = self.request.query_params.get("folder", "inbox")
        qs = qs.filter(sender=user) if folder == "sent" else qs.filter(recipient=user)
        if self.request.query_params.get("unread") == "true":
            qs = qs.filter(read_at__isnull=True)
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        recipient_id = data.get("recipient")
        if not recipient_id:
            return Response({"recipient": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        sender_school = user_school(request.user)
        school = sender_school
        recipient_queryset = scoped_users(sender_school) if sender_school else scoped_users()
        recipient = get_object_or_404(recipient_queryset, pk=recipient_id)
        if recipient == request.user:
            return Response({"recipient": ["You cannot send a message to yourself."]}, status=status.HTTP_400_BAD_REQUEST)
        if is_admin(request.user) and data.get("school"):
            school = get_object_or_404(School, pk=data["school"])
            recipient = get_object_or_404(scoped_users(school), pk=recipient_id)
        if school is None:
            school = recipient_school(recipient)
        if school is None:
            return Response({"detail": "The recipient is not associated with an institution."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data={**data, "school": str(school.pk), "recipient": str(recipient.pk)})
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user)
        notify(recipient=recipient, school=school, title=f"New message from {request.user.get_full_name() or request.user.email}", body=serializer.instance.subject, notification_type=Notification.Type.MESSAGE, link="/communication")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        message = get_object_or_404(self.get_queryset().filter(recipient=request.user), pk=pk)
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
        contacts = scoped_users(school).exclude(pk=request.user.pk)
        search = request.query_params.get("search", "").strip()
        if search:
            contacts = contacts.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
        return Response(CommunicationContactSerializer(contacts.order_by("first_name", "last_name"), many=True).data)

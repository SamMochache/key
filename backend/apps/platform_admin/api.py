from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessments.models.ai_narrative_report import AINarrativeReport
from apps.identity.models import User
from apps.parents.models import Parent
from apps.schools.models import School, SchoolAdministrator
from apps.students.models import Student
from apps.teachers.models import Teacher

from .models import AuditLog, PlatformSetting
from .permissions import IsPlatformAdmin


class PlatformSummaryView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        schools = School.objects.filter(is_deleted=False)
        return Response(
            {
                "institutions": schools.count(),
                "active_institutions": schools.filter(is_active=True).count(),
                "students": Student.objects.filter(is_active=True).count(),
                "teachers": Teacher.objects.filter(status="ACTIVE").count(),
                "parents": Parent.objects.filter(is_active=True).count(),
                "users": User.objects.filter(is_active=True).count(),
                "ai_reports": AINarrativeReport.objects.count(),
            }
        )


class PlatformUserListView(APIView):
    permission_classes = [IsPlatformAdmin]

    @staticmethod
    def _role(user):
        if user.is_superuser or (
            user.is_staff and getattr(user, "school_admin_profile", None) is None
        ):
            return "platform_admin"
        if getattr(user, "school_admin_profile", None) is not None:
            return "admin"
        if getattr(user, "teacher_profile", None) is not None:
            return "teacher"
        if getattr(user, "student_profile", None) is not None:
            return "student"
        if getattr(user, "parent_profile", None) is not None:
            return "parent"
        return "user"

    @classmethod
    def _serialize(cls, user):
        school = None
        for relation in (
            "school_admin_profile",
            "teacher_profile",
            "student_profile",
            "parent_profile",
        ):
            profile = getattr(user, relation, None)
            if profile is not None:
                school = getattr(profile, "school", None)
                break
        return {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": cls._role(user),
            "school_id": str(school.id) if school else None,
            "school_name": school.name if school else None,
            "is_active": user.is_active,
            "status": user.status,
            "last_login": user.last_login,
            "created_at": user.created_at,
        }

    def get(self, request):
        queryset = User.objects.all().prefetch_related(
            "school_admin_profile__school",
            "teacher_profile__school",
            "student_profile__school",
            "parent_profile__school",
        )
        search = request.query_params.get("search", "").strip()
        role = request.query_params.get("role", "").strip()
        school_id = request.query_params.get("school", "").strip()
        active = request.query_params.get("active", "").strip()

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )
        if school_id:
            queryset = queryset.filter(
                Q(school_admin_profile__school_id=school_id)
                | Q(teacher_profile__school_id=school_id)
                | Q(student_profile__school_id=school_id)
                | Q(parent_profile__school_id=school_id)
            ).distinct()
        if active in {"true", "false"}:
            queryset = queryset.filter(is_active=active == "true")

        users = [self._serialize(user) for user in queryset.order_by("first_name", "last_name")]
        if role:
            users = [user for user in users if user["role"] == role]

        paginator = LimitOffsetPagination()
        page = paginator.paginate_queryset(users, request, view=self)
        return paginator.get_paginated_response(page)


class PlatformUserStatusView(APIView):
    permission_classes = [IsPlatformAdmin]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user == request.user:
            return Response(
                {"detail": "You cannot deactivate your own platform account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_superuser or (
            user.is_staff and getattr(user, "school_admin_profile", None) is None
        ):
            return Response(
                {"detail": "Platform administrator accounts cannot be changed here."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "is_active" not in request.data:
            return Response({"detail": "is_active is required."}, status=status.HTTP_400_BAD_REQUEST)

        is_active = bool(request.data["is_active"])
        user.is_active = is_active
        user.status = "ACTIVE" if is_active else "SUSPENDED"
        user.save(update_fields=["is_active", "status", "updated_at"])
        AuditLog.objects.create(
            actor=request.user,
            school=_school_for_user(user),
            action="USER_ACTIVATED" if is_active else "USER_SUSPENDED",
            resource_type="user",
            resource_id=str(user.id),
            metadata={"email": user.email},
        )
        return Response(PlatformUserListView._serialize(user))


class PlatformAuditLogView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        queryset = AuditLog.objects.select_related("actor", "school")
        action = request.query_params.get("action", "").strip()
        if action:
            queryset = queryset.filter(action=action)
        paginator = LimitOffsetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = [
            {
                "id": str(item.id),
                "action": item.action,
                "resource_type": item.resource_type,
                "resource_id": item.resource_id,
                "actor": item.actor.full_name if item.actor else "System",
                "actor_email": item.actor.email if item.actor else None,
                "school": item.school.name if item.school else None,
                "metadata": item.metadata,
                "created_at": item.created_at,
            }
            for item in page
        ]
        return paginator.get_paginated_response(data)


DEFAULT_SETTINGS = {
    "platform_name": ("KEY", "Display name used by the platform control plane."),
    "default_timezone": ("Africa/Nairobi", "Default timezone applied when a new institution omits one."),
    "default_country": ("Kenya", "Default country applied when a new institution omits one."),
}


class PlatformSettingsView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        result = {}
        for key, (default, description) in DEFAULT_SETTINGS.items():
            setting, _ = PlatformSetting.objects.get_or_create(
                key=key,
                defaults={"value": default, "description": description},
            )
            result[key] = setting.value
        return Response(result)

    def patch(self, request):
        unknown = set(request.data) - set(DEFAULT_SETTINGS)
        if unknown:
            return Response(
                {"detail": f"Unsupported settings: {', '.join(sorted(unknown))}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for key, value in request.data.items():
            setting, _ = PlatformSetting.objects.get_or_create(
                key=key,
                defaults={"value": DEFAULT_SETTINGS[key][0], "description": DEFAULT_SETTINGS[key][1]},
            )
            setting.value = value
            setting.save(update_fields=["value", "updated_at"])
            AuditLog.objects.create(
                actor=request.user,
                action="PLATFORM_SETTING_UPDATED",
                resource_type="platform_setting",
                resource_id=key,
                metadata={"value": value},
            )
        return self.get(request)


class InstitutionOverviewView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request, school_id):
        try:
            school = School.objects.get(pk=school_id)
        except School.DoesNotExist:
            return Response({"detail": "Institution not found."}, status=status.HTTP_404_NOT_FOUND)

        users = PlatformUserListView._serialize
        school_users = User.objects.filter(
            Q(school_admin_profile__school=school)
            | Q(teacher_profile__school=school)
            | Q(student_profile__school=school)
            | Q(parent_profile__school=school)
        ).distinct().prefetch_related(
            "school_admin_profile__school",
            "teacher_profile__school",
            "student_profile__school",
            "parent_profile__school",
        )
        AuditLog.objects.create(
            actor=request.user,
            school=school,
            action="INSTITUTION_VIEWED",
            resource_type="school",
            resource_id=str(school.id),
            metadata={"mode": "platform_overview"},
        )
        return Response(
            {
                "school": {
                    "id": str(school.id),
                    "name": school.name,
                    "short_name": school.short_name,
                    "email": school.email,
                    "phone_number": school.phone_number,
                    "address": school.address,
                    "city": school.city,
                    "country": school.country,
                    "timezone": school.timezone,
                    "is_active": school.is_active,
                    "created_at": school.created_at,
                    "updated_at": school.updated_at,
                },
                "users": [users(user) for user in school_users],
            }
        )


class SchoolAdministratorCreateView(APIView):
    permission_classes = [IsPlatformAdmin]

    @transaction.atomic
    def post(self, request, school_id):
        try:
            school = School.objects.get(pk=school_id)
        except School.DoesNotExist:
            return Response({"detail": "Institution not found."}, status=status.HTTP_404_NOT_FOUND)

        required = ("email", "first_name", "last_name", "password")
        missing = [field for field in required if not request.data.get(field)]
        if missing:
            return Response(
                {"detail": f"Missing required fields: {', '.join(missing)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        password = str(request.data["password"])
        if len(password) < 8:
            return Response({"detail": "Password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)
        email = str(request.data["email"]).strip().lower()
        if User.objects.filter(email=email).exists():
            return Response({"detail": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=str(request.data["first_name"]).strip(),
            last_name=str(request.data["last_name"]).strip(),
            phone_number=str(request.data.get("phone_number", "")).strip(),
            timezone=school.timezone,
        )
        administrator = SchoolAdministrator.objects.create(user=user, school=school)
        AuditLog.objects.create(
            actor=request.user,
            school=school,
            action="SCHOOL_ADMIN_CREATED",
            resource_type="school_administrator",
            resource_id=str(administrator.id),
            metadata={"email": user.email},
        )
        return Response(
            {
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "school_id": str(school.id),
                "school_name": school.name,
                "role": "admin",
                "is_active": user.is_active,
            },
            status=status.HTTP_201_CREATED,
        )


def _school_for_user(user):
    for relation in (
        "school_admin_profile",
        "teacher_profile",
        "student_profile",
        "parent_profile",
    ):
        profile = getattr(user, relation, None)
        if profile is not None:
            return getattr(profile, "school", None)
    return None

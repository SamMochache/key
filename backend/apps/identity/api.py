from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _data(self, request):
        user = request.user
        photo_url = None
        if user.profile_photo:
            try:
                photo_url = request.build_absolute_uri(user.profile_photo.url)
            except ValueError:
                photo_url = None

        data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "initials": user.initials,
            "profile_photo": photo_url,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "timezone": user.timezone,
            "status": user.status,
        }
        school_admin = getattr(user, "school_admin_profile", None)
        if school_admin is not None and school_admin.is_active:
            data["role"] = "admin"
            data["school_id"] = str(school_admin.school_id)
        elif user.is_superuser or user.is_staff:
            data["role"] = "admin"
            data["platform_admin"] = True
        elif hasattr(user, "teacher_profile"):
            data["role"] = "teacher"
            data["school_id"] = str(user.teacher_profile.school_id)
        elif hasattr(user, "parent_profile"):
            data["role"] = "parent"
            data["school_id"] = str(user.parent_profile.school_id)
        elif hasattr(user, "student_profile"):
            data["role"] = "student"
            data["school_id"] = str(user.student_profile.school_id)
        else:
            data["role"] = "user"
        return data

    def get(self, request):
        return Response(self._data(request))

    def patch(self, request):
        user = request.user
        allowed = {"first_name", "last_name", "phone_number", "preferred_language", "timezone"}
        unknown = set(request.data.keys()) - allowed
        if unknown:
            return Response(
                {"detail": f"These fields cannot be changed here: {', '.join(sorted(unknown))}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        changed = allowed.intersection(request.data.keys())
        for field in changed:
            value = request.data[field]
            if not isinstance(value, str):
                return Response({field: "This field must be a string."}, status=status.HTTP_400_BAD_REQUEST)
            setattr(user, field, value.strip())
        if changed:
            user.save(update_fields=list(changed))
        return Response(self._data(request))


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not all(isinstance(value, str) and value for value in (current_password, new_password, confirm_password)):
            return Response(
                {"detail": "Current password, new password, and confirmation are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.check_password(current_password):
            return Response({"current_password": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({"confirm_password": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(new_password, request.user)
        except DjangoValidationError as exc:
            return Response({"new_password": exc.messages}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Password changed successfully."})

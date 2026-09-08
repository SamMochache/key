from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
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
        return Response(data)

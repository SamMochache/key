from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "initials": user.initials,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "timezone": user.timezone,
            "status": user.status,
        }
        if user.is_superuser or user.is_staff:
            data["role"] = "admin"
        elif hasattr(user, "teacher_profile"):
            data["role"] = "teacher"
            data["school_id"] = str(user.teacher_profile.school_id)
        elif hasattr(user, "student_profile"):
            data["role"] = "student"
            data["school_id"] = str(user.student_profile.school_id)
        else:
            data["role"] = "user"
        return Response(data)

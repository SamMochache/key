from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api import ChangePasswordView, CurrentUserView

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
]

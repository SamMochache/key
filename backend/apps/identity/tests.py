from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class IdentityApiTests(APITestCase):
    def setUp(self):
        self.password = "Strong-test-password-123!"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Regular",
            last_name="User",
        )
        self.staff = User.objects.create_superuser(
            email="admin@example.com",
            password=self.password,
            first_name="System",
            last_name="Admin",
        )

    def test_current_user_requires_authentication(self):
        response = self.client.get(reverse("current-user"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_returns_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.user.id))
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["role"], "user")

    def test_staff_user_is_reported_as_admin(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "admin")

    def test_token_endpoint_accepts_email_and_password(self):
        response = self.client.post(
            reverse("token-obtain-pair"),
            {"email": self.user.email, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_endpoint_rejects_invalid_password(self):
        response = self.client.post(
            reverse("token-obtain-pair"),
            {"email": self.user.email, "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

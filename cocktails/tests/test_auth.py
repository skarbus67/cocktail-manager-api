"""Integration tests for registration, login and logout."""

from django.contrib.auth.models import User

from .base import BaseTestCase


class RegisterTests(BaseTestCase):
    def test_register_creates_user(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="alice")
        self.assertTrue(user.check_password("sup3r-secret"))

        payload = response.json()
        self.assertEqual(payload["message"], "Registered successfully.")
        self.assertEqual(payload["user_id"], user.id)

    def test_register_requires_username_and_password(self):
        response = self.post_json("/api/auth/register/", {"username": "alice"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Username and password are required.")

    def test_register_rejects_duplicate_username(self):
        self.create_user("alice")
        response = self.register()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"], "A user with that username already exists."
        )

    def test_register_invalid_json(self):
        response = self.client.post(
            "/api/auth/register/", data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON format.")


class LoginTests(BaseTestCase):
    def setUp(self):
        self.create_user("alice")

    def test_login_success(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Logged in successfully.")

    def test_login_invalid_credentials(self):
        response = self.login(password="wrong-password")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "Invalid credentials.")

    def test_login_invalid_json(self):
        response = self.client.post(
            "/api/auth/login/", data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON format.")


class LogoutTests(BaseTestCase):
    def test_logout(self):
        self.create_user("alice")
        self.login()
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Logged out successfully.")

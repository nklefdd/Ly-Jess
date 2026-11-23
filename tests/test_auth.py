import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User

from .conftest import PASSWORD

pytestmark = pytest.mark.django_db

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
REFRESH_URL = "/api/auth/refresh"
LOGOUT_URL = "/api/auth/logout"
ME_URL = "/api/auth/me"


def register_payload(**overrides):
    data = {
        "username": "taras",
        "email": "taras@example.com",
        "phone": "+380501234567",
        "password": PASSWORD,
        "password_confirmation": PASSWORD,
    }
    data.update(overrides)
    return data


class TestRegister:
    def test_success(self, api_client):
        response = api_client.post(REGISTER_URL, register_payload(), format="json")

        assert response.status_code == 201
        body = response.json()
        assert body["username"] == "taras"
        assert body["role"] == "user"
        assert "password" not in body
        assert User.objects.get(username="taras").check_password(PASSWORD)

    def test_passwords_do_not_match(self, api_client):
        payload = register_payload(password_confirmation="Other!Pass123")
        response = api_client.post(REGISTER_URL, payload, format="json")

        assert response.status_code == 400
        assert "password_confirmation" in response.json()["error"]["details"]

    def test_weak_password(self, api_client):
        payload = register_payload(password="12345678", password_confirmation="12345678")
        response = api_client.post(REGISTER_URL, payload, format="json")

        assert response.status_code == 400
        assert "password" in response.json()["error"]["details"]

    def test_username_taken(self, api_client, user):
        response = api_client.post(
            REGISTER_URL, register_payload(username=user.username), format="json"
        )

        assert response.status_code == 400
        assert "username" in response.json()["error"]["details"]

    def test_email_taken(self, api_client, user):
        response = api_client.post(
            REGISTER_URL, register_payload(email=user.email), format="json"
        )

        assert response.status_code == 400
        assert "email" in response.json()["error"]["details"]

    def test_invalid_phone(self, api_client):
        response = api_client.post(
            REGISTER_URL, register_payload(phone="0501234567"), format="json"
        )

        assert response.status_code == 400
        assert "phone" in response.json()["error"]["details"]

    def test_missing_fields(self, api_client):
        response = api_client.post(REGISTER_URL, {}, format="json")

        assert response.status_code == 400
        details = response.json()["error"]["details"]
        assert {"username", "email", "password"} <= set(details)

    def test_cannot_register_as_admin(self, api_client):
        payload = register_payload(is_staff=True, role="admin")
        response = api_client.post(REGISTER_URL, payload, format="json")

        assert response.status_code == 201
        assert response.json()["role"] == "user"
        assert not User.objects.get(username="taras").is_staff


class TestLogin:
    def test_success(self, api_client, user):
        response = api_client.post(
            LOGIN_URL, {"username": user.username, "password": PASSWORD}, format="json"
        )

        assert response.status_code == 200
        assert {"access", "refresh"} <= set(response.json())

    def test_wrong_password(self, api_client, user):
        response = api_client.post(
            LOGIN_URL, {"username": user.username, "password": "wrong-pass"}, format="json"
        )

        assert response.status_code == 401
        assert response.json()["error"]["status"] == 401

    def test_blocked_user(self, api_client, user):
        user.is_active = False
        user.save()

        response = api_client.post(
            LOGIN_URL, {"username": user.username, "password": PASSWORD}, format="json"
        )

        assert response.status_code == 401


class TestRefreshAndLogout:
    def test_refresh_returns_new_access(self, api_client, user):
        refresh = RefreshToken.for_user(user)

        response = api_client.post(REFRESH_URL, {"refresh": str(refresh)}, format="json")

        assert response.status_code == 200
        assert "access" in response.json()

    def test_refresh_with_invalid_token(self, api_client):
        response = api_client.post(REFRESH_URL, {"refresh": "not-a-token"}, format="json")

        assert response.status_code == 401

    def test_logout_blacklists_refresh(self, auth_client, user):
        refresh = str(RefreshToken.for_user(user))

        response = auth_client.post(LOGOUT_URL, {"refresh": refresh}, format="json")
        assert response.status_code == 204

        response = auth_client.post(REFRESH_URL, {"refresh": refresh}, format="json")
        assert response.status_code == 401

    def test_logout_twice(self, auth_client, user):
        refresh = str(RefreshToken.for_user(user))
        auth_client.post(LOGOUT_URL, {"refresh": refresh}, format="json")

        response = auth_client.post(LOGOUT_URL, {"refresh": refresh}, format="json")

        assert response.status_code == 400

    def test_logout_without_token(self, api_client):
        response = api_client.post(LOGOUT_URL, {"refresh": "x"}, format="json")

        assert response.status_code == 401


class TestMe:
    def test_requires_auth(self, api_client):
        response = api_client.get(ME_URL)

        assert response.status_code == 401
        assert response.json()["error"]["status"] == 401

    def test_get_profile(self, auth_client, user):
        response = auth_client.get(ME_URL)

        assert response.status_code == 200
        assert response.json()["username"] == user.username

    def test_update_profile(self, auth_client, user):
        response = auth_client.patch(
            ME_URL, {"first_name": "Олена", "phone": "+380671112233"}, format="json"
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "Олена"
        assert user.phone == "+380671112233"

    def test_invalid_phone(self, auth_client):
        response = auth_client.patch(ME_URL, {"phone": "123"}, format="json")

        assert response.status_code == 400

    def test_cannot_change_username(self, auth_client, user):
        auth_client.patch(ME_URL, {"username": "hacker"}, format="json")

        user.refresh_from_db()
        assert user.username == "olena"

    def test_invalid_token(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Bearer broken")

        response = api_client.get(ME_URL)

        assert response.status_code == 401

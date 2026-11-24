import pytest

pytestmark = pytest.mark.django_db

USERS_URL = "/api/users"


def detail_url(pk):
    return f"{USERS_URL}/{pk}"


class TestUserList:
    def test_requires_auth(self, api_client):
        assert api_client.get(USERS_URL).status_code == 401

    def test_regular_user_forbidden(self, auth_client):
        response = auth_client.get(USERS_URL)

        assert response.status_code == 403
        assert response.json()["error"]["status"] == 403

    def test_admin_sees_all_users(self, admin_client, user, admin):
        response = admin_client.get(USERS_URL)

        assert response.status_code == 200
        usernames = {item["username"] for item in response.json()}
        assert usernames == {user.username, admin.username}


class TestUserDetail:
    def test_get_user(self, admin_client, user):
        response = admin_client.get(detail_url(user.pk))

        assert response.status_code == 200
        assert response.json()["role"] == "user"

    def test_not_found(self, admin_client):
        response = admin_client.get(detail_url(9999))

        assert response.status_code == 404
        assert response.json()["error"]["status"] == 404

    def test_make_admin(self, admin_client, user):
        response = admin_client.patch(detail_url(user.pk), {"role": "admin"}, format="json")

        assert response.status_code == 200
        assert response.json()["role"] == "admin"
        user.refresh_from_db()
        assert user.is_staff

    def test_block_user(self, admin_client, user):
        response = admin_client.patch(detail_url(user.pk), {"is_active": False}, format="json")

        assert response.status_code == 200
        user.refresh_from_db()
        assert not user.is_active

    def test_invalid_role(self, admin_client, user):
        response = admin_client.patch(detail_url(user.pk), {"role": "boss"}, format="json")

        assert response.status_code == 400

    def test_admin_cannot_demote_self(self, admin_client, admin):
        response = admin_client.patch(detail_url(admin.pk), {"role": "user"}, format="json")

        assert response.status_code == 400
        admin.refresh_from_db()
        assert admin.is_staff

    def test_regular_user_cannot_change_roles(self, auth_client, user):
        response = auth_client.patch(detail_url(user.pk), {"role": "admin"}, format="json")

        assert response.status_code == 403

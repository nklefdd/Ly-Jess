import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User

PASSWORD = "River!Amber872"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="olena", email="olena@example.com", password=PASSWORD
    )


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="admin", email="admin@example.com", password=PASSWORD, is_staff=True
    )


def client_for(user):
    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def auth_client(user):
    return client_for(user)


@pytest.fixture
def admin_client(admin):
    return client_for(admin)

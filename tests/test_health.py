from rest_framework.test import APIClient


def test_health_returns_ok():
    response = APIClient().get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_url_returns_404():
    response = APIClient().get("/api/unknown")

    assert response.status_code == 404

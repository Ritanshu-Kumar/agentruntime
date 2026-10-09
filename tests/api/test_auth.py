from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_health_is_public():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200


def test_runs_requires_api_key():
    client = TestClient(app)

    response = client.get(
        "/runs/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"


def test_invalid_api_key_is_rejected():
    client = TestClient(app)

    response = client.get(
        "/runs/00000000-0000-0000-0000-000000000000",
        headers={
            "X-API-Key": "wrong-key",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"


def test_valid_api_key_reaches_application():
    client = TestClient(app)

    settings = get_settings()

    response = client.get(
        "/runs/00000000-0000-0000-0000-000000000000",
        headers={
            "X-API-Key": settings.api_key,
        },
    )

    # Authentication succeeded; the repository then reports that
    # this particular run does not exist.
    assert response.status_code == 404
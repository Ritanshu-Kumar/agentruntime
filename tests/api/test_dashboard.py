
from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_page_is_available():
    response = TestClient(app).get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AgentRuntime" in response.text
    assert 'id="taskForm"' in response.text


def test_dashboard_does_not_embed_default_api_key():
    response = TestClient(app).get("/dashboard")

    assert response.status_code == 200
    assert "development-api-key" not in response.text

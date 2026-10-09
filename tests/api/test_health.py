from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api import health
from app.main import app


def test_readiness_returns_ready(monkeypatch):
    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, statement):
            assert str(statement) == "SELECT 1"

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    monkeypatch.setattr(
        health,
        "get_database_engine",
        lambda: FakeEngine(),
    )

    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ok",
    }


def test_readiness_returns_503_when_database_is_down(
    monkeypatch,
):
    class FakeEngine:
        def connect(self):
            raise OperationalError(
                "SELECT 1",
                {},
                Exception("database unavailable"),
            )

    monkeypatch.setattr(
        health,
        "get_database_engine",
        lambda: FakeEngine(),
    )

    response = TestClient(app).get("/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Database is unavailable"
    )
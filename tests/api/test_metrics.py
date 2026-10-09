from fastapi.testclient import TestClient

from app.api.dependencies import get_agent_runner
from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.tool_executor import ToolExecutor
from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder
from app.domain.tools.registry import ToolRegistry
from app.infrastructure.runs_repository import InMemoryRunRepository
from app.main import app


def make_runner():
    recorder = EventRecorder()

    runner = AgentRunner(
        llm=FakeLLM(
            [FinalAnswer(content="Test answer")]
        ),
        tool_executor=ToolExecutor(
            registry=ToolRegistry(),
            permissions=set(),
        ),
        run_repository=InMemoryRunRepository(),
        event_recorder=recorder,
    )

    return runner


def test_metrics_requires_api_key():
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 401


def test_metrics_reports_recorded_run_events():
    runner = make_runner()
    app.dependency_overrides[get_agent_runner] = lambda: runner

    try:
        runner.run("Test task")

        response = TestClient(app).get(
            "/metrics",
            headers={
                "X-API-Key": "development-api-key",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "ok"
        assert body["runs"]["started"] == 1
        assert body["runs"]["completed"] == 1
        assert body["runs"]["failed"] == 0
        assert body["repository_configured"] is True
    finally:
        app.dependency_overrides.clear()
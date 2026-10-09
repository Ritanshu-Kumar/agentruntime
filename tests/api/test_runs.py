from uuid import UUID

from fastapi.testclient import TestClient

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.tool_executor import ToolExecutor
from app.domain.runs.models import Run
from app.domain.runs.repository import RunRepository
from app.domain.tools.registry import ToolRegistry
from app.main import app


class FakeRunRepository(RunRepository):
    def __init__(self):
        self.runs: dict[UUID, Run] = {}

    def create(self, run: Run) -> Run:
        self.runs[run.id] = run.model_copy(deep=True)
        return run

    def get(self, run_id: UUID) -> Run | None:
        run = self.runs.get(run_id)

        if run is None:
            return None

        return run.model_copy(deep=True)

    def save(self, run: Run) -> Run:
        self.runs[run.id] = run.model_copy(deep=True)
        return run


def make_runner():
    repository = FakeRunRepository()

    llm = FakeLLM(
        [
            FinalAnswer(
                content="Hello from AgentRuntime"
            )
        ]
    )

    executor = ToolExecutor(
        registry=ToolRegistry(),
        permissions=set(),
    )

    return AgentRunner(
        llm=llm,
        tool_executor=executor,
        run_repository=repository,
    )


def test_health():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_create_run():
    runner = make_runner()
    app.state.agent_runner = runner

    client = TestClient(app)

    response = client.post(
        "/runs",
        json={
            "task": "Say hello",
        },
        headers={
        "X-API-Key": "development-api-key",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["task"] == "Say hello"
    assert body["status"] == "completed"
    assert body["answer"] == "Hello from AgentRuntime"


def test_get_run():
    runner = make_runner()
    app.state.agent_runner = runner

    client = TestClient(app)

    created = client.post(
        "/runs",
        json={
            "task": "Say hello",
        },
        headers={"X-API-Key": "development-api-key"},
    )

    assert created.status_code == 201

    run_id = created.json()["id"]

    response = client.get(
        f"/runs/{run_id}",
        headers={
        "X-API-Key": "development-api-key",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == run_id
    assert body["status"] == "completed"


def test_get_missing_run():
    runner = make_runner()
    app.state.agent_runner = runner

    client = TestClient(app)

    response = client.get(
        "/runs/00000000-0000-0000-0000-000000000000",
        headers={"X-API-Key": "development-api-key"},
    )

    assert response.status_code == 404
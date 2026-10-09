
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_agent_runner
from app.application.agent import AgentRunner
from app.application.llm import FakeLLM
from app.application.tool_executor import ToolExecutor
from app.domain.tools.registry import ToolRegistry
from app.infrastructure.runs_repository import InMemoryRunRepository


API_KEY = "development-api-key"
HEADERS = {"X-API-Key": API_KEY}


def test_failed_run_does_not_prevent_a_later_run():
    app.state.agent_runner = None
    client = TestClient(app)

    failing_runner = AgentRunner(
        llm=FakeLLM(responses=[]),
        tool_executor=ToolExecutor(
            registry=ToolRegistry(),
            permissions=set(),
        ),
        run_repository=InMemoryRunRepository(),
    )

    app.dependency_overrides[get_agent_runner] = lambda: failing_runner

    try:
        failed_response = client.post(
            "/runs",
            json={"task": "Trigger a model failure"},
            headers=HEADERS,
        )

        assert failed_response.status_code == 201
        assert failed_response.json()["status"] == "failed"

        failed_runs = list(failing_runner.run_repository._runs.values())
        assert len(failed_runs) == 1
        assert failed_runs[0].status == "failed"

        app.dependency_overrides.clear()
        app.state.agent_runner = None

        recovered_response = client.post(
            "/runs",
            json={"task": "A fresh request"},
            headers=HEADERS,
        )

        assert recovered_response.status_code == 201
        assert recovered_response.json()["status"] == "completed"
    finally:
        app.dependency_overrides.clear()
        app.state.agent_runner = None


def test_multiple_run_requests_succeed():
    app.state.agent_runner = None
    client = TestClient(app)

    try:
        for task in ("First task", "Second task"):
            response = client.post(
                "/runs",
                json={"task": task},
                headers=HEADERS,
            )

            assert response.status_code == 201
            assert response.json()["task"] == task
            assert response.json()["status"] == "completed"
    finally:
        app.state.agent_runner = None


def test_concurrent_run_requests_keep_results_separate():
    app.state.agent_runner = None
    client = TestClient(app)

    tasks = [f"Concurrent task {i}" for i in range(10)]

    def submit(task: str):
        return client.post(
            "/runs",
            json={"task": task},
            headers=HEADERS,
        )

    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(executor.map(submit, tasks))

        assert all(response.status_code == 201 for response in responses)

        results = [response.json() for response in responses]

        assert {result["task"] for result in results} == set(tasks)
        assert len({result["id"] for result in results}) == len(tasks)
        assert all(result["status"] == "completed" for result in results)
    finally:
        app.state.agent_runner = None

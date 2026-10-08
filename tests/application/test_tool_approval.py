from uuid import uuid4

import pytest
from pydantic import BaseModel

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.approval.errors import ApprovalRequiredError
from app.domain.approval.repository import InMemoryApprovalRepository
from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder
from app.domain.runs.models import RunStatus
from app.domain.tools.base import Tool, ToolResult
from app.domain.tools.permissions import Permission
from app.domain.tools.registry import ToolRegistry
from app.domain.tools.safety import SafetyLevel
from app.infrastructure.runs_repository import InMemoryRunRepository


class SensitiveInput(BaseModel):
    value: str


class SensitiveTool(Tool[SensitiveInput]):
    name = "sensitive_tool"
    description = "Sensitive test tool"
    input_schema = SensitiveInput
    permissions = frozenset({Permission.PYTHON_EXECUTE})
    safety_level = SafetyLevel.SENSITIVE

    def __init__(self):
        self.calls = 0

    def execute(self, arguments: SensitiveInput) -> ToolResult:
        self.calls += 1
        return ToolResult.ok(arguments.value)


def make_sensitive_executor(
    approval_repository: InMemoryApprovalRepository | None = None,
    event_recorder: EventRecorder | None = None,
) -> ToolExecutor:
    registry = ToolRegistry()
    registry.register(SensitiveTool())
    return ToolExecutor(
        registry=registry,
        permissions={Permission.PYTHON_EXECUTE.value},
        event_recorder=event_recorder,
        approval_repository=approval_repository,
    )


def test_sensitive_tool_creates_approval_request():
    tool = SensitiveTool()
    registry = ToolRegistry()
    registry.register(tool)

    approvals = InMemoryApprovalRepository()
    recorder = EventRecorder()
    run_id = uuid4()

    executor = ToolExecutor(
        registry=registry,
        permissions={Permission.PYTHON_EXECUTE.value},
        event_recorder=recorder,
        approval_repository=approvals,
    )

    with pytest.raises(ApprovalRequiredError) as exc_info:
        executor.execute(
            ToolCall(
                tool_name="sensitive_tool",
                arguments={"value": "secret"},
            ),
            run_id=run_id,
        )

    request = exc_info.value.request
    assert request.run_id == run_id
    assert request.tool_name == "sensitive_tool"
    assert request.arguments == {"value": "secret"}
    assert request.status.value == "pending"

    stored = approvals.get(request.id)
    assert stored is not None
    assert stored.id == request.id
    assert tool.calls == 0

    events = recorder.events(run_id)
    assert any(
        event.event_type == EventType.APPROVAL_REQUESTED
        for event in events
    )


def test_sensitive_tool_without_repository_still_requires_approval() -> None:
    executor = make_sensitive_executor()

    with pytest.raises(ApprovalRequiredError) as error:
        executor.execute(
            ToolCall(
                tool_name="sensitive_tool",
                arguments={"value": "review me"},
            ),
            run_id=uuid4(),
        )

    assert error.value.request.tool_name == "sensitive_tool"


def test_agent_persists_run_waiting_for_approval() -> None:
    approval_repository = InMemoryApprovalRepository()
    event_recorder = EventRecorder()
    run_repository = InMemoryRunRepository()
    runner = AgentRunner(
        llm=FakeLLM(
            responses=[
                ToolCall(
                    tool_name="sensitive_tool",
                    arguments={"value": "review me"},
                )
            ]
        ),
        tool_executor=make_sensitive_executor(
            approval_repository,
            event_recorder,
        ),
        run_repository=run_repository,
        event_recorder=event_recorder,
    )

    with pytest.raises(ApprovalRequiredError):
        runner.run("Perform a sensitive action")

    run = run_repository.get(runner.last_run_id)
    assert run is not None
    assert run.status == RunStatus.WAITING_APPROVAL

    events = run_repository.get_execution_events(run.id)
    assert [event.event_type for event in events] == [
        EventType.RUN_STARTED,
        EventType.MODEL_CALLED,
        EventType.APPROVAL_REQUESTED,
    ]
    assert approval_repository.get_pending_for_run(run.id)
from uuid import uuid4

import pytest
from pydantic import BaseModel

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer, ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.approval.errors import ApprovalRequiredError
from app.domain.approval.repository import InMemoryApprovalRepository
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

    def __init__(self) -> None:
        self.calls = 0
        self.received = None

    def execute(self, arguments: SensitiveInput) -> ToolResult:
        self.calls += 1
        self.received = arguments
        return ToolResult.ok(arguments.value)


def make_agent(
    llm: FakeLLM,
    approvals: InMemoryApprovalRepository | None = None,
    tool: SensitiveTool | None = None,
):
    registry = ToolRegistry()
    tool = tool or SensitiveTool()
    registry.register(tool)
    approvals = approvals or InMemoryApprovalRepository()
    recorder = EventRecorder()
    run_repository = InMemoryRunRepository()
    executor = ToolExecutor(
        registry=registry,
        permissions={Permission.PYTHON_EXECUTE.value},
        event_recorder=recorder,
        approval_repository=approvals,
    )
    agent = AgentRunner(
        llm=llm,
        tool_executor=executor,
        run_repository=run_repository,
        event_recorder=recorder,
        approval_repository=approvals,
    )
    return agent, approvals, tool, run_repository


def test_approval_resume_executes_after_approval() -> None:
    llm = FakeLLM(
        [
            ToolCall(tool_name="sensitive_tool", arguments={"value": "secret"}),
            FinalAnswer(content="done"),
        ]
    )
    agent, approvals, tool, run_repository = make_agent(llm)

    with pytest.raises(ApprovalRequiredError):
        agent.run("do something sensitive")

    run = run_repository.get(agent.last_run_id)
    assert run is not None
    assert run.status == RunStatus.WAITING_APPROVAL

    request = approvals.get_pending_for_run(run.id)[0]
    request.approve("Approved by test")
    approvals.save(request)

    result = agent.resume(request.id)

    assert result == "done"
    assert tool.calls == 1
    run = run_repository.get(run.id)
    assert run is not None
    assert run.status == RunStatus.COMPLETED


def test_approval_resume_rejects_and_marks_run_failed() -> None:
    llm = FakeLLM(
        [
            ToolCall(tool_name="sensitive_tool", arguments={"value": "secret"}),
        ]
    )
    agent, approvals, tool, run_repository = make_agent(llm)

    with pytest.raises(ApprovalRequiredError):
        agent.run("do something sensitive")

    run = run_repository.get(agent.last_run_id)
    assert run is not None
    request = approvals.get_pending_for_run(run.id)[0]
    request.reject("Denied by test")
    approvals.save(request)

    with pytest.raises(ValueError, match="rejected"):
        agent.resume(request.id)

    assert tool.calls == 0
    run = run_repository.get(run.id)
    assert run is not None
    assert run.status == RunStatus.FAILED


def test_approval_resume_pending_request_raises_error() -> None:
    llm = FakeLLM(
        [
            ToolCall(tool_name="sensitive_tool", arguments={"value": "secret"}),
        ]
    )
    agent, approvals, tool, run_repository = make_agent(llm)

    with pytest.raises(ApprovalRequiredError):
        agent.run("do something sensitive")

    run = run_repository.get(agent.last_run_id)
    assert run is not None
    request = approvals.get_pending_for_run(run.id)[0]

    with pytest.raises(ValueError, match="still pending"):
        agent.resume(request.id)

    assert tool.calls == 0

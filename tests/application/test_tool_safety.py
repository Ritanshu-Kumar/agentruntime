from uuid import uuid4

from pydantic import BaseModel

from app.application.llm import ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder
from app.domain.tools.base import Tool, ToolResult
from app.domain.tools.permissions import Permission
from app.domain.tools.registry import ToolRegistry
from app.domain.tools.safety import SafetyLevel


class DangerousInput(BaseModel):
    value: str


class DangerousTool(Tool[DangerousInput]):
    name = "dangerous_tool"
    description = "A dangerous test tool"
    input_schema = DangerousInput
    permissions = frozenset({Permission.PYTHON_EXECUTE})
    safety_level = SafetyLevel.DANGEROUS

    calls = 0

    def execute(self, arguments: DangerousInput) -> ToolResult:
        self.calls += 1
        return ToolResult.ok(arguments.value)


class SafeInput(BaseModel):
    value: str


class SafeTool(Tool[SafeInput]):
    name = "safe_tool"
    description = "A safe test tool"
    input_schema = SafeInput
    permissions = frozenset()
    safety_level = SafetyLevel.SAFE

    calls = 0

    def execute(self, arguments: SafeInput) -> ToolResult:
        self.calls += 1
        return ToolResult.ok(arguments.value)


def test_dangerous_tool_is_blocked_before_execution():
    tool = DangerousTool()
    registry = ToolRegistry()
    registry.register(tool)

    recorder = EventRecorder()
    run_id = uuid4()

    executor = ToolExecutor(
        registry=registry,
        permissions={Permission.PYTHON_EXECUTE.value},
        event_recorder=recorder,
    )

    result = executor.execute(
        ToolCall(
            tool_name="dangerous_tool",
            arguments={"value": "secret"},
        ),
        run_id=run_id,
    )

    assert not result.success
    assert "Safety policy denied" in result.content
    assert tool.calls == 0

    events = recorder.events(run_id)

    blocked_events = [
        event
        for event in events
        if event.event_type == EventType.TOOL_BLOCKED
    ]

    assert len(blocked_events) == 1

    event = blocked_events[0]

    assert event.metadata["tool_name"] == "dangerous_tool"
    assert event.metadata["safety_level"] == "dangerous"
    assert event.metadata["reason"] == "blocked by safety policy"


def test_safe_tool_executes_normally():
    tool = SafeTool()
    registry = ToolRegistry()
    registry.register(tool)

    executor = ToolExecutor(
        registry=registry,
        permissions=set(),
    )

    result = executor.execute(
        ToolCall(
            tool_name="safe_tool",
            arguments={"value": "hello"},
        )
    )

    assert result.success
    assert result.content == "hello"
    assert tool.calls == 1
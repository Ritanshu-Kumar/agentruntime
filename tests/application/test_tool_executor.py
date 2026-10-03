from pydantic import BaseModel

from app.application.retry import RetryPolicy
from app.application.llm import ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.tools import Permission, Tool, ToolRegistry, ToolResult
from app.domain.tools.errors import ToolTransientError


class ExampleInput(BaseModel):
    value: int


class ExampleTool(Tool[ExampleInput]):
    name = "example"
    description = "Example tool"
    input_schema = ExampleInput
    permissions = frozenset({Permission.FILESYSTEM_READ})

    def execute(self, arguments: ExampleInput) -> ToolResult:
        return ToolResult.ok(arguments.value * 2)


def make_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ExampleTool())
    return registry


def test_executes_tool() -> None:
    executor = ToolExecutor(
        make_registry(),
        {Permission.FILESYSTEM_READ.value},
    )

    result = executor.execute(
        ToolCall(
            tool_name="example",
            arguments={"value": 5},
        )
    )

    assert result.success is True
    assert result.content == "10"


def test_denies_missing_permission() -> None:
    executor = ToolExecutor(make_registry(), set())

    result = executor.execute(
        ToolCall(
            tool_name="example",
            arguments={"value": 5},
        )
    )

    assert result.success is False
    assert "Permission denied" in result.content

def test_executor_retries_failed_tool():
    class FlakyTool:
        name = "flaky"
        permissions = set()

        def __init__(self):
            self.calls = 0

        def validate_input(self, arguments):
            return arguments

        def execute(self, arguments):
            self.calls += 1

            if self.calls < 3:
                raise ToolTransientError("temporary failure")

            return ToolResult.ok("success")

    tool = FlakyTool()

    registry = ToolRegistry()
    registry.register(tool)

    executor = ToolExecutor(
        registry,
        set(),
        RetryPolicy(max_attempts=3),
    )

    result = executor.execute(
        ToolCall(
            tool_name="flaky",
            arguments={},
        )
    )

    assert result.success is True
    assert result.content == "success"
    assert tool.calls == 3

def test_executor_does_not_retry_permission_failure():
    class ProtectedTool:
        name = "protected"
        permissions = {"filesystem.read"}

        def validate_input(self, arguments):
            return arguments

        def execute(self, arguments):
            raise AssertionError("Tool should never execute")

    registry = ToolRegistry()
    registry.register(ProtectedTool())

    executor = ToolExecutor(
        registry,
        set(),
        RetryPolicy(max_attempts=3),
    )

    result = executor.execute(
        ToolCall(
            tool_name="protected",
            arguments={},
        )
    )

    assert result.success is False
    assert "Permission denied" in result.content

def test_executor_stops_after_max_attempts():
    class AlwaysFailingTool:
        name = "failing"
        permissions = set()

        def __init__(self):
            self.calls = 0

        def validate_input(self, arguments):
            return arguments

        def execute(self, arguments):
            self.calls += 1
            raise ToolTransientError("permanent failure")

    tool = AlwaysFailingTool()

    registry = ToolRegistry()
    registry.register(tool)

    executor = ToolExecutor(
        registry,
        set(),
        RetryPolicy(max_attempts=3),
    )

    result = executor.execute(
        ToolCall(
            tool_name="failing",
            arguments={},
        )
    )

    assert result.success is False
    assert tool.calls == 3
from pydantic import BaseModel

from app.application.llm import ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.tools import Permission, Tool, ToolRegistry, ToolResult


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
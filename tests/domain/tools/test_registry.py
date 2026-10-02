import pytest
from pydantic import BaseModel

from app.domain.tools import (
    DuplicateToolError,
    Tool,
    ToolNotFoundError,
    ToolRegistry,
    ToolResult,
)


class ExampleInput(BaseModel):
    value: int


class ExampleTool(Tool[ExampleInput]):
    name = "example"
    description = "Test tool"
    input_schema = ExampleInput

    def execute(self, arguments: ExampleInput) -> ToolResult:
        return ToolResult.ok(arguments.value)


def test_register_and_get() -> None:
    registry = ToolRegistry()
    tool = ExampleTool()

    registry.register(tool)

    assert registry.get("example") is tool


def test_contains() -> None:
    registry = ToolRegistry()

    assert registry.contains("example") is False

    registry.register(ExampleTool())

    assert registry.contains("example") is True


def test_list() -> None:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    assert registry.list() == ["example"]


def test_duplicate_registration_fails() -> None:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    with pytest.raises(DuplicateToolError):
        registry.register(ExampleTool())


def test_unknown_tool_fails() -> None:
    registry = ToolRegistry()

    with pytest.raises(ToolNotFoundError):
        registry.get("missing")
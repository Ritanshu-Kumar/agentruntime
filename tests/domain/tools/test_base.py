import pytest
from pydantic import BaseModel

from app.domain.tools import Permission, Tool, ToolResult, ToolValidationError


class ExampleInput(BaseModel):
    value: int


class ExampleTool(Tool[ExampleInput]):
    name = "example"
    description = "A test tool."
    input_schema = ExampleInput
    permissions = frozenset({Permission.FILESYSTEM_READ})

    def execute(self, arguments: ExampleInput) -> ToolResult:
        return ToolResult.ok(arguments.value * 2)


def test_tool_validates_arguments() -> None:
    arguments = ExampleTool().validate_input({"value": 21})
    assert arguments.value == 21


def test_tool_rejects_invalid_arguments() -> None:
    with pytest.raises(ToolValidationError):
        ExampleTool().validate_input({"value": "not-an-int"})


def test_tool_result_success() -> None:
    result = ToolResult.ok("hello")
    assert result.success is True
    assert result.output == "hello"
    assert result.error is None


def test_tool_result_failure() -> None:
    result = ToolResult.failure("something went wrong")
    assert result.success is False
    assert result.output is None
    assert result.error == "something went wrong"


def test_tool_declares_permissions() -> None:
    assert Permission.FILESYSTEM_READ in ExampleTool().permissions

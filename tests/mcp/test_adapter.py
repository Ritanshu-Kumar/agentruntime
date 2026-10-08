from typing import Any

import pytest

from app.domain.mcp.adapter import MCPToolAdapter
from app.domain.mcp.models import MCPToolCallResult, MCPToolDefinition
from app.domain.tools.errors import ToolValidationError


class FakeMCPClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> MCPToolCallResult:
        self.calls.append((tool_name, arguments))
        return MCPToolCallResult(
            success=True,
            content=[
                {"type": "text", "text": "4"},
            ],
        )


def make_tool() -> tuple[MCPToolAdapter, FakeMCPClient]:
    definition = MCPToolDefinition(
        name="calculator",
        description="Calculate something",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
                "precision": {"type": "integer"},
            },
            "required": ["expression"],
        },
    )

    client = FakeMCPClient()
    tool = MCPToolAdapter(client, definition)
    return tool, client


def test_adapter_exposes_mcp_tool() -> None:
    tool, _ = make_tool()

    assert tool.name == "calculator"
    assert tool.description == "Calculate something"


def test_adapter_validates_required_arguments() -> None:
    tool, _ = make_tool()

    with pytest.raises(
        ToolValidationError,
        match="Missing required MCP argument: expression",
    ):
        tool.validate_input({})


def test_adapter_validates_argument_types() -> None:
    tool, _ = make_tool()

    with pytest.raises(
        ToolValidationError,
        match="Invalid type for MCP argument 'expression'",
    ):
        tool.validate_input({"expression": 123})


def test_adapter_calls_mcp_client() -> None:
    tool, client = make_tool()

    result = tool.execute({"expression": "2 + 2"})

    assert result.success is True
    assert result.output == "4"
    assert client.calls == [
        ("calculator", {"expression": "2 + 2"})
    ]


def test_adapter_converts_mcp_failure() -> None:
    definition = MCPToolDefinition(
        name="broken",
        input_schema={"type": "object"},
    )

    class FailingClient:
        def call_tool(
            self,
            tool_name: str,
            arguments: dict[str, Any],
        ) -> MCPToolCallResult:
            return MCPToolCallResult(
                success=False,
                error="remote failure",
            )

    tool = MCPToolAdapter(FailingClient(), definition)

    result = tool.execute({})

    assert result.success is False
    assert result.error == "remote failure"

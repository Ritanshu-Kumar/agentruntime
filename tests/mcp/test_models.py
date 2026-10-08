from app.domain.mcp.models import MCPToolCallResult, MCPToolDefinition


def test_mcp_tool_definition() -> None:
    tool = MCPToolDefinition(
        name="calculator",
        description="Perform calculations",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
            },
            "required": ["expression"],
        },
    )

    assert tool.name == "calculator"
    assert tool.input_schema["type"] == "object"


def test_mcp_tool_call_result() -> None:
    result = MCPToolCallResult(
        success=True,
        content=[
            {
                "type": "text",
                "text": "42",
            }
        ],
    )

    assert result.success is True
    assert result.content[0]["text"] == "42"

from typing import Any

from app.domain.mcp.client import MCPClient
from app.domain.mcp.models import MCPToolCallResult, MCPToolDefinition


class FakeMCPClient(MCPClient):
    def list_tools(self) -> list[MCPToolDefinition]:
        return [
            MCPToolDefinition(
                name="calculator",
                description="Calculate",
                input_schema={
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"},
                    },
                },
            )
        ]

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> MCPToolCallResult:
        assert tool_name == "calculator"
        assert arguments == {"expression": "2 + 2"}
        return MCPToolCallResult(
            success=True,
            content=[
                {
                    "type": "text",
                    "text": "4",
                }
            ],
        )


def test_fake_mcp_client_lists_and_calls_tools() -> None:
    client = FakeMCPClient()

    tools = client.list_tools()
    result = client.call_tool(
        "calculator",
        {"expression": "2 + 2"},
    )

    assert len(tools) == 1
    assert tools[0].name == "calculator"
    assert result.success is True
    assert result.content[0]["text"] == "4"

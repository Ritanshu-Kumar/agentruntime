import sys
from pathlib import Path

from app.domain.mcp.stdio_client import StdioMCPClient


SERVER = Path(__file__).with_name(
    "stdio_server.py"
)


def make_client():
    return StdioMCPClient(
        [
            sys.executable,
            str(SERVER),
        ]
    )


def test_stdio_mcp_client_lists_tools():
    client = make_client()

    try:
        tools = client.list_tools()

        assert len(tools) == 1
        assert tools[0].name == "add"
        assert tools[0].description == "Add two integers"
    finally:
        client.close()


def test_stdio_mcp_client_calls_tool():
    client = make_client()

    try:
        result = client.call_tool(
            "add",
            {
                "a": 20,
                "b": 22,
            },
        )

        assert result.success is True
        assert result.content == [
            {
                "type": "text",
                "text": "42",
            }
        ]
    finally:
        client.close()


def test_stdio_mcp_client_records_server_info():
    client = make_client()

    try:
        client.list_tools()

        assert client.server_info is not None
        assert client.server_info["serverInfo"]["name"] == (
            "test-mcp-server"
        )
    finally:
        client.close()
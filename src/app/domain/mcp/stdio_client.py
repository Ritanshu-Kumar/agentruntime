import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from app.domain.mcp.client import MCPClient
from app.domain.mcp.models import (
    MCPToolCallResult,
    MCPToolDefinition,
)


class StdioMCPClient(MCPClient):
    """
    Minimal MCP client using the legacy handshake lifecycle
    over newline-delimited stdio.

    This is intentionally small so the protocol mechanics remain visible.
    """

    PROTOCOL_VERSION = "2025-11-25"

    def __init__(
        self,
        command: list[str],
        *,
        cwd: str | Path | None = None,
    ) -> None:
        self.command = command
        self.cwd = str(cwd) if cwd is not None else None
        self.process: subprocess.Popen[str] | None = None
        self._next_id = 1
        self.server_info: dict[str, Any] | None = None

    def connect(self) -> None:
        if self.process is not None:
            return

        self.process = subprocess.Popen(
            self.command,
            cwd=self.cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        response = self._request(
            "initialize",
            {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": "agentruntime",
                    "version": "0.1.0",
                },
            },
        )

        result = response.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("MCP initialize returned an invalid result")

        self.server_info = result

        self._notify("notifications/initialized")

    def list_tools(self) -> list[MCPToolDefinition]:
        self._ensure_connected()

        response = self._request("tools/list", {})
        result = response.get("result", {})

        return [
            MCPToolDefinition(
                name=tool["name"],
                description=tool.get("description", ""),
                input_schema=tool.get(
                    "inputSchema",
                    {},
                ),
            )
            for tool in result.get("tools", [])
        ]

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> MCPToolCallResult:
        self._ensure_connected()

        response = self._request(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments,
            },
        )

        if "error" in response:
            error = response["error"]
            return MCPToolCallResult(
                success=False,
                error=str(error),
            )

        result = response.get("result", {})

        return MCPToolCallResult(
            success=not result.get("isError", False),
            content=result.get("content", []),
            structured_content=result.get(
                "structuredContent"
            ),
            error=(
                "MCP tool returned an error"
                if result.get("isError", False)
                else None
            ),
        )

    def close(self) -> None:
        if self.process is None:
            return

        if self.process.stdin:
            self.process.stdin.close()

        self.process.terminate()
        self.process.wait(timeout=5)
        self.process = None

    def _ensure_connected(self) -> None:
        if self.process is None:
            self.connect()

    def _request(
        self,
        method: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if self.process is None:
            raise RuntimeError("MCP client is not connected")

        if self.process.stdin is None:
            raise RuntimeError("MCP stdin is unavailable")

        if self.process.stdout is None:
            raise RuntimeError("MCP stdout is unavailable")

        request_id = self._next_id
        self._next_id += 1

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }

        self.process.stdin.write(
            json.dumps(message) + "\n"
        )
        self.process.stdin.flush()

        line = self.process.stdout.readline()

        if not line:
            raise RuntimeError(
                "MCP server closed stdout unexpectedly"
            )

        response = json.loads(line)

        if response.get("id") != request_id:
            raise RuntimeError(
                "MCP response id does not match request id"
            )

        return response

    def _notify(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> None:
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("MCP client is not connected")

        message = {
            "jsonrpc": "2.0",
            "method": method,
        }

        if params is not None:
            message["params"] = params

        self.process.stdin.write(
            json.dumps(message) + "\n"
        )
        self.process.stdin.flush()
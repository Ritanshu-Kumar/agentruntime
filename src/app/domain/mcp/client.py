from abc import ABC, abstractmethod
from typing import Any

from app.domain.mcp.models import MCPToolCallResult, MCPToolDefinition


class MCPClient(ABC):
    """Transport-independent interface to an MCP server."""

    @abstractmethod
    def list_tools(self) -> list[MCPToolDefinition]:
        raise NotImplementedError

    @abstractmethod
    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> MCPToolCallResult:
        raise NotImplementedError

from typing import Any

from pydantic import BaseModel, Field


class MCPToolDefinition(BaseModel):
    """Description of a tool exposed by an MCP server."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)


class MCPToolCallResult(BaseModel):
    """Normalized result returned by an MCP tool call."""

    success: bool
    content: list[dict[str, Any]] = Field(default_factory=list)
    structured_content: dict[str, Any] | None = None
    error: str | None = None

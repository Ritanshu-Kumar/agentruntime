from typing import Any

from app.domain.mcp.client import MCPClient
from app.domain.mcp.models import MCPToolDefinition
from app.domain.tools.base import Tool, ToolResult
from app.domain.tools.errors import ToolValidationError
from app.domain.tools.permissions import Permission
from app.domain.tools.safety import SafetyLevel


class MCPToolAdapter(Tool[dict[str, Any]]):
    """Expose an MCP tool through the AgentRuntime Tool interface."""

    def __init__(
        self,
        client: MCPClient,
        definition: MCPToolDefinition,
        *,
        permissions: frozenset[Permission] = frozenset(),
        safety_level: SafetyLevel = SafetyLevel.SAFE,
    ) -> None:
        self.client = client
        self.name = definition.name
        self.description = definition.description
        self.input_schema = definition.input_schema
        self.permissions = permissions
        self.safety_level = safety_level

    def validate_input(
        self,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(arguments, dict):
            raise ToolValidationError("MCP tool arguments must be an object")

        schema = self.input_schema
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for field in required:
            if field not in arguments:
                raise ToolValidationError(
                    f"Missing required MCP argument: {field}"
                )

        for field, value in arguments.items():
            if field not in properties:
                continue

            expected_type = properties[field].get("type")
            if expected_type is None:
                continue

            if not self._matches_type(value, expected_type):
                raise ToolValidationError(
                    f"Invalid type for MCP argument '{field}': "
                    f"expected {expected_type}"
                )

        return arguments

    @staticmethod
    def _matches_type(value: Any, expected_type: str) -> bool:
        if expected_type == "string":
            return isinstance(value, str)
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
            )
        if expected_type == "boolean":
            return isinstance(value, bool)
        if expected_type == "array":
            return isinstance(value, list)
        if expected_type == "object":
            return isinstance(value, dict)
        if expected_type == "null":
            return value is None
        return True

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        result = self.client.call_tool(self.name, arguments)

        if not result.success:
            return ToolResult.failure(
                result.error or f"MCP tool '{self.name}' failed"
            )

        if result.structured_content is not None:
            return ToolResult.ok(result.structured_content)

        text_parts = []
        for item in result.content:
            if item.get("type") == "text":
                text_parts.append(str(item.get("text", "")))
            else:
                text_parts.append(str(item))

        return ToolResult.ok("\n".join(text_parts))

from app.domain.tools.base import Tool
from app.domain.tools.errors import (
    DuplicateToolError,
    ToolNotFoundError,
)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise DuplicateToolError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(
                f"Tool not found: {name}"
            ) from exc

    def contains(self, name: str) -> bool:
        return name in self._tools

    def list(self) -> list[str]:
        return list(self._tools.keys())
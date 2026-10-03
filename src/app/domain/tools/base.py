from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from app.domain.tools.errors import ToolValidationError
from app.domain.tools.permissions import Permission

InputModelT = TypeVar("InputModelT", bound=BaseModel)


@dataclass(frozen=True)
class ToolResult:
    """Normalized result returned by a tool execution."""

    success: bool
    output: Any = None
    error: str | None = None

    @classmethod
    def ok(cls, output: Any = None) -> "ToolResult":
        return cls(success=True, output=output)

    @classmethod
    def failure(cls, error: str) -> "ToolResult":
        return cls(success=False, error=error)


class Tool(ABC, Generic[InputModelT]):
    """Base contract implemented by every AgentRuntime tool."""

    name: str
    description: str
    input_schema: type[InputModelT]
    permissions: frozenset[Permission] = frozenset()

    def validate_input(
        self, arguments: dict[str, Any]
    ) -> InputModelT | dict[str, Any]:
        if not isinstance(self.input_schema, type) or not issubclass(
            self.input_schema, BaseModel
        ):
            return arguments

        try:
            return self.input_schema.model_validate(arguments)
        except ValidationError as exc:
            raise ToolValidationError(str(exc)) from exc

    @abstractmethod
    def execute(self, arguments: InputModelT) -> ToolResult:
        raise NotImplementedError

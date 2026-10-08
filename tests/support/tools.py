from pydantic import BaseModel

from app.domain.tools import Permission, Tool, ToolResult


class ExampleInput(BaseModel):
    value: int


class ExampleTool(Tool[ExampleInput]):
    name = "example"
    description = "Example tool"
    input_schema = ExampleInput
    permissions = frozenset({Permission.FILESYSTEM_READ})

    def execute(self, arguments: ExampleInput) -> ToolResult:
        return ToolResult.ok(arguments.value * 2)
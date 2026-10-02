from app.application.llm import ToolCall
from app.application.messages import ToolMessage
from app.domain.tools import ToolRegistry


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        permissions: set[str],
    ) -> None:
        self.registry = registry
        self.permissions = permissions

    def execute(self, call: ToolCall) -> ToolMessage:
        tool = self.registry.get(call.tool_name)

        required = {permission.value for permission in tool.permissions}

        if not required.issubset(self.permissions):
            missing = required - self.permissions
            return ToolMessage(
                tool_name=call.tool_name,
                success=False,
                content=f"Permission denied: {sorted(missing)}",
            )

        arguments = tool.validate_input(call.arguments)
        result = tool.execute(arguments)

        return ToolMessage(
            tool_name=call.tool_name,
            success=result.success,
            content=(
                str(result.output)
                if result.success
                else result.error or "Tool execution failed."
            ),
        )
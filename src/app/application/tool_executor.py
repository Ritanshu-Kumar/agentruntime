from uuid import UUID

from app.application.failure_policy import is_retryable_error
from app.application.llm import ToolCall
from app.application.messages import ToolMessage
from app.application.retry import RetryPolicy
from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder
from app.domain.tools.errors import PermissionDeniedError
from app.domain.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        permissions: set[str],
        retry_policy: RetryPolicy | None = None,
        event_recorder: EventRecorder | None = None,
    ):
        self.registry = registry
        self.permissions = permissions
        self.retry_policy = retry_policy or RetryPolicy()
        self.event_recorder = event_recorder

    def execute(
        self,
        tool_call: ToolCall,
        run_id: UUID | None = None,
    ) -> ToolMessage:
        try:
            tool = self.registry.get(tool_call.tool_name)

            required_permissions = {
                permission.value if hasattr(permission, "value") else permission
                for permission in tool.permissions
            }

            granted_permissions = {
                permission.value if hasattr(permission, "value") else permission
                for permission in self.permissions
            }

            if not required_permissions.issubset(granted_permissions):
                raise PermissionDeniedError(
                    f"Permission denied for tool '{tool.name}'"
                )

            validated_arguments = tool.validate_input(tool_call.arguments)

        except Exception as exc:
            return ToolMessage(
                tool_name=tool_call.tool_name,
                success=False,
                content=str(exc),
            )

        for attempt in range(1, self.retry_policy.max_attempts + 1):
            try:
                result = tool.execute(validated_arguments)

                if result.success:
                    return ToolMessage(
                        tool_name=tool.name,
                        success=True,
                        content=(
                            str(result.output)
                            if result.output is not None
                            else ""
                        ),
                    )

                error = RuntimeError(
                    result.error or "Tool execution failed"
                )

                if not self.retry_policy.should_retry(
                    attempt,
                    is_retryable_error(error),
                ):
                    return ToolMessage(
                        tool_name=tool.name,
                        success=False,
                        content=str(error),
                    )

                if self.event_recorder and run_id is not None:
                    self.event_recorder.record(
                        run_id,
                        EventType.RETRY,
                        {
                            "tool_name": tool.name,
                            "attempt": attempt,
                            "max_attempts": self.retry_policy.max_attempts,
                            "error": str(error),
                        },
                    )

            except Exception as exc:
                if not self.retry_policy.should_retry(
                    attempt,
                    is_retryable_error(exc),
                ):
                    return ToolMessage(
                        tool_name=tool.name,
                        success=False,
                        content=str(exc),
                    )

                if self.event_recorder and run_id is not None:
                    self.event_recorder.record(
                        run_id,
                        EventType.RETRY,
                        {
                            "tool_name": tool.name,
                            "attempt": attempt,
                            "max_attempts": self.retry_policy.max_attempts,
                            "error": str(exc),
                        },
                    )

        return ToolMessage(
            tool_name=tool.name,
            success=False,
            content="Tool execution failed after maximum retry attempts",
        )
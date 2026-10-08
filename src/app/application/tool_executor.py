from uuid import UUID

from app.application.failure_policy import is_retryable_error
from app.application.llm import ToolCall
from app.application.messages import ToolMessage
from app.application.retry import RetryPolicy
from app.domain.approval.errors import ApprovalRequiredError
from app.domain.approval.models import ApprovalRequest, ApprovalStatus
from app.domain.approval.repository import ApprovalRepository
from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder
from app.domain.tools.registry import ToolRegistry
from app.domain.tools.errors import (
    PermissionDeniedError,
    SafetyDeniedError,
)
from app.domain.tools.safety import SafetyLevel, SafetyPolicy


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        permissions: set[str],
        retry_policy: RetryPolicy | None = None,
        event_recorder: EventRecorder | None = None,
        safety_policy: SafetyPolicy | None = None,
        approval_repository: ApprovalRepository | None = None,
    ):
        self.registry = registry
        self.permissions = permissions
        self.retry_policy = retry_policy or RetryPolicy()
        self.event_recorder = event_recorder
        self.safety_policy = safety_policy or SafetyPolicy()
        self.approval_repository = approval_repository

    def execute_approved(self, request: ApprovalRequest) -> ToolMessage:
        if request.status != ApprovalStatus.APPROVED:
            raise ValueError("Approval request has not been approved")

        tool_call = ToolCall(
            tool_name=request.tool_name,
            arguments=request.arguments,
        )
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

                error = RuntimeError(result.error or "Tool execution failed")
                if not self.retry_policy.should_retry(
                    attempt,
                    is_retryable_error(error),
                ):
                    return ToolMessage(
                        tool_name=tool.name,
                        success=False,
                        content=str(error),
                    )

                if self.event_recorder and request.run_id is not None:
                    self.event_recorder.record(
                        request.run_id,
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

                if self.event_recorder and request.run_id is not None:
                    self.event_recorder.record(
                        request.run_id,
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

    def execute(
        self,
        tool_call: ToolCall,
        run_id: UUID | None = None,
    ) -> ToolMessage:
        try:
            tool = self.registry.get(tool_call.tool_name)

            safety_level = getattr(
                tool,
                "safety_level",
                SafetyLevel.SAFE,
            )

            if not self.safety_policy.allows(safety_level):
                if safety_level == SafetyLevel.SENSITIVE:
                    if self.approval_repository is None:
                        raise ApprovalRequiredError(
                            ApprovalRequest(
                                run_id=run_id,
                                tool_name=tool.name,
                                arguments=tool_call.arguments,
                                reason="Sensitive tool requires human approval",
                            )
                        )
                    if run_id is None:
                        raise ValueError(
                            "Sensitive tool execution requires a run_id"
                        )
                    request = ApprovalRequest(
                        run_id=run_id,
                        tool_name=tool.name,
                        arguments=tool_call.arguments,
                        reason="Sensitive tool requires human approval",
                    )
                    self.approval_repository.create(request)
                    if self.event_recorder:
                        self.event_recorder.record(
                            run_id,
                            EventType.APPROVAL_REQUESTED,
                            {
                                "approval_id": str(request.id),
                                "tool_name": tool.name,
                                "safety_level": safety_level.value,
                            },
                        )
                    raise ApprovalRequiredError(request)

                if self.event_recorder and run_id is not None:
                    self.event_recorder.record(
                        run_id,
                        EventType.TOOL_BLOCKED,
                        {
                            "tool_name": tool.name,
                            "safety_level": safety_level.value,
                            "reason": "blocked by safety policy",
                        },
                    )

                raise SafetyDeniedError(
                    f"Safety policy denied tool '{tool.name}' "
                    f"at level '{safety_level.value}'"
                )

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

        except ApprovalRequiredError:
            raise
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

            except ApprovalRequiredError:
                raise
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
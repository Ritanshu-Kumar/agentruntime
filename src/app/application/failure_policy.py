from app.domain.tools.errors import (
    PermissionDeniedError,
    ToolNotFoundError,
    ToolTimeoutError,
    ToolTransientError,
    ToolValidationError,
)


def is_retryable_error(error: Exception) -> bool:
    if isinstance(
        error,
        (
            PermissionDeniedError,
            ToolNotFoundError,
            ToolValidationError,
        ),
    ):
        return False

    if isinstance(error, (ToolTimeoutError, ToolTransientError)):
        return True

    return False
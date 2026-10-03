from app.domain.tools.errors import (
    PermissionDeniedError,
    ToolNotFoundError,
    ToolTimeoutError,
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

    if isinstance(error, ToolTimeoutError):
        return True

    return True
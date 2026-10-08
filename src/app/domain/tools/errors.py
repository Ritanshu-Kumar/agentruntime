class ToolError(Exception):
    pass


class ToolValidationError(ToolError):
    pass


class PermissionDeniedError(ToolError):
    pass


class ToolNotFoundError(ToolError):
    pass


class DuplicateToolError(ToolError):
    pass


class ToolTransientError(ToolError):
    pass


class ToolTimeoutError(ToolTransientError):
    pass

class SafetyDeniedError(ToolError):
    pass
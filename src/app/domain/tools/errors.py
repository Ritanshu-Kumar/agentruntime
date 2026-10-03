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

class ToolTimeoutError(ToolError):
    pass
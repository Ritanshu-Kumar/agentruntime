import subprocess
import sys

from pydantic import BaseModel

from app.domain.tools import Permission, Tool, ToolResult
from app.domain.tools.errors import ToolTimeoutError


class PythonInput(BaseModel):
    code: str


class PythonExecutorTool(Tool[PythonInput]):
    name = "execute_python"
    description = "Execute Python code in a subprocess."
    input_schema = PythonInput
    permissions = frozenset({Permission.PYTHON_EXECUTE})

    def __init__(self, timeout: float = 5.0, timeout_seconds: float | None = None) -> None:
        self.timeout = timeout if timeout_seconds is None else timeout_seconds

    def execute(self, arguments: PythonInput | dict[str, str]) -> ToolResult:
        if isinstance(arguments, dict):
            arguments = self.validate_input(arguments)

        try:
            result = subprocess.run(
                [sys.executable, "-c", arguments.code],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise ToolTimeoutError("Python execution timed out.") from exc
        except OSError as exc:
            return ToolResult.failure(
                f"Unable to start Python process: {exc}"
            )

        output = result.stdout

        if result.stderr:
            output += result.stderr

        if result.returncode != 0:
            return ToolResult.failure(output.strip())

        return ToolResult.ok(output)
import subprocess
import sys

from pydantic import BaseModel

from app.domain.tools import Permission, Tool, ToolResult


class PythonInput(BaseModel):
    code: str


class PythonExecutorTool(Tool[PythonInput]):
    name = "execute_python"
    description = "Execute Python code in a subprocess."
    input_schema = PythonInput
    permissions = frozenset({Permission.PYTHON_EXECUTE})

    def __init__(self, timeout: float = 5.0) -> None:
        self.timeout = timeout

    def execute(self, arguments: PythonInput) -> ToolResult:
        try:
            result = subprocess.run(
                [sys.executable, "-c", arguments.code],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return ToolResult.failure("Python execution timed out.")
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
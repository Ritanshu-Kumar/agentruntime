from app.domain.tools import Permission
from app.infrastructure.tools.python_executor import PythonExecutorTool


def test_executes_python() -> None:
    tool = PythonExecutorTool()

    arguments = tool.validate_input(
        {"code": "print(2 + 3)"}
    )

    result = tool.execute(arguments)

    assert result.success is True
    assert result.output.strip() == "5"


def test_captures_stderr() -> None:
    tool = PythonExecutorTool()

    arguments = tool.validate_input(
        {
            "code": (
                "import sys; "
                "sys.stderr.write('warning')"
            )
        }
    )

    result = tool.execute(arguments)

    assert result.success is True
    assert "warning" in result.output


def test_runtime_error_fails() -> None:
    tool = PythonExecutorTool()

    arguments = tool.validate_input(
        {"code": "raise RuntimeError('boom')"}
    )

    result = tool.execute(arguments)

    assert result.success is False
    assert "RuntimeError" in result.error
    assert "boom" in result.error


def test_timeout() -> None:
    tool = PythonExecutorTool(timeout=0.1)

    arguments = tool.validate_input(
        {
            "code": (
                "import time; "
                "time.sleep(2)"
            )
        }
    )

    result = tool.execute(arguments)

    assert result.success is False
    assert result.error == "Python execution timed out."


def test_declares_python_permission() -> None:
    tool = PythonExecutorTool()

    assert Permission.PYTHON_EXECUTE in tool.permissions
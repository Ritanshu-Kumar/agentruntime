from pathlib import Path

from pydantic import BaseModel

from app.domain.tools import Permission, Tool, ToolResult


class ReadFileInput(BaseModel):
    path: str


class ReadFileTool(Tool[ReadFileInput]):
    name = "read_file"
    description = "Read a UTF-8 text file."
    input_schema = ReadFileInput
    permissions = frozenset({Permission.FILESYSTEM_READ})

    def __init__(self, allowed_root: Path) -> None:
        self.allowed_root = allowed_root.resolve()

    def execute(self, arguments: ReadFileInput) -> ToolResult:
        path = (self.allowed_root / arguments.path).resolve()

        try:
            path.relative_to(self.allowed_root)
        except ValueError:
            return ToolResult.failure("Path is outside the allowed root.")

        if not path.exists():
            return ToolResult.failure("File does not exist.")

        if not path.is_file():
            return ToolResult.failure("Path is not a file.")

        try:
            return ToolResult.ok(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            return ToolResult.failure("File is not valid UTF-8.")
        except OSError as exc:
            return ToolResult.failure(f"Unable to read file: {exc}")
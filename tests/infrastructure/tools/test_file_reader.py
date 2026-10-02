from pathlib import Path

from app.domain.tools import Permission
from app.infrastructure.tools.file_reader import ReadFileTool


def test_reads_file(tmp_path: Path) -> None:
    file = tmp_path / "hello.txt"
    file.write_text("hello world", encoding="utf-8")

    tool = ReadFileTool(tmp_path)

    arguments = tool.validate_input({"path": "hello.txt"})
    result = tool.execute(arguments)

    assert result.success is True
    assert result.output == "hello world"


def test_rejects_path_outside_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()

    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    tool = ReadFileTool(allowed)

    arguments = tool.validate_input({"path": "../secret.txt"})
    result = tool.execute(arguments)

    assert result.success is False
    assert result.error == "Path is outside the allowed root."


def test_missing_file(tmp_path: Path) -> None:
    tool = ReadFileTool(tmp_path)

    arguments = tool.validate_input({"path": "missing.txt"})
    result = tool.execute(arguments)

    assert result.success is False
    assert result.error == "File does not exist."


def test_directory_is_rejected(tmp_path: Path) -> None:
    directory = tmp_path / "directory"
    directory.mkdir()

    tool = ReadFileTool(tmp_path)

    arguments = tool.validate_input({"path": "directory"})
    result = tool.execute(arguments)

    assert result.success is False
    assert result.error == "Path is not a file."


def test_invalid_utf8_is_rejected(tmp_path: Path) -> None:
    file = tmp_path / "binary.dat"
    file.write_bytes(b"\xff\xfe\xfd")

    tool = ReadFileTool(tmp_path)

    arguments = tool.validate_input({"path": "binary.dat"})
    result = tool.execute(arguments)

    assert result.success is False
    assert result.error == "File is not valid UTF-8."


def test_declares_filesystem_permission(tmp_path: Path) -> None:
    tool = ReadFileTool(tmp_path)

    assert Permission.FILESYSTEM_READ in tool.permissions
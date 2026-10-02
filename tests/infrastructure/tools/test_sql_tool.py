import sqlite3
from pathlib import Path

from app.domain.tools import Permission
from app.infrastructure.tools.sql_tool import SQLTool


def create_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE users (id INTEGER, name TEXT)"
        )
        connection.executemany(
            "INSERT INTO users VALUES (?, ?)",
            [(1, "Alice"), (2, "Bob")],
        )


def test_select_query(tmp_path: Path) -> None:
    database = tmp_path / "test.db"
    create_database(database)

    tool = SQLTool(str(database))

    arguments = tool.validate_input(
        {"query": "SELECT id, name FROM users ORDER BY id"}
    )

    result = tool.execute(arguments)

    assert result.success is True
    assert result.output == {
        "columns": ["id", "name"],
        "rows": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ],
    }


def test_empty_result(tmp_path: Path) -> None:
    database = tmp_path / "test.db"
    create_database(database)

    tool = SQLTool(str(database))

    arguments = tool.validate_input(
        {"query": "SELECT * FROM users WHERE id = 999"}
    )

    result = tool.execute(arguments)

    assert result.success is True
    assert result.output["rows"] == []


def test_invalid_sql(tmp_path: Path) -> None:
    database = tmp_path / "test.db"
    create_database(database)

    tool = SQLTool(str(database))

    arguments = tool.validate_input(
        {"query": "SELECT * FROM missing_table"}
    )

    result = tool.execute(arguments)

    assert result.success is False
    assert "no such table" in result.error


def test_declares_database_read_permission(
    tmp_path: Path,
) -> None:
    tool = SQLTool(str(tmp_path / "test.db"))

    assert Permission.DATABASE_READ in tool.permissions
import sqlite3

from pydantic import BaseModel

from app.domain.tools import Permission, Tool, ToolResult


class SQLInput(BaseModel):
    query: str


class SQLTool(Tool[SQLInput]):
    name = "query_sql"
    description = "Execute a read-only SQL query against SQLite."
    input_schema = SQLInput
    permissions = frozenset({Permission.DATABASE_READ})

    def __init__(self, database: str) -> None:
        self.database = database

    def execute(self, arguments: SQLInput) -> ToolResult:
        try:
            with sqlite3.connect(self.database) as connection:
                cursor = connection.execute(arguments.query)

                columns = [
                    description[0]
                    for description in cursor.description or []
                ]

                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return ToolResult.ok(
                    {
                        "columns": columns,
                        "rows": rows,
                    }
                )

        except sqlite3.Error as exc:
            return ToolResult.failure(str(exc))
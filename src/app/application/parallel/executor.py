from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

from app.application.llm import ToolCall
from app.application.messages import ToolMessage
from app.application.tool_executor import ToolExecutor


class ParallelToolExecutor:
    """Execute independent tool calls concurrently."""

    def __init__(
        self,
        tool_executor: ToolExecutor,
        max_workers: int = 4,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        self.tool_executor = tool_executor
        self.max_workers = max_workers

    def execute(
        self,
        tool_calls: list[ToolCall],
        run_id: UUID | None = None,
    ) -> list[ToolMessage]:
        if not tool_calls:
            return []

        with ThreadPoolExecutor(
            max_workers=min(
                self.max_workers,
                len(tool_calls),
            )
        ) as executor:
            futures = [
                executor.submit(
                    self.tool_executor.execute,
                    tool_call,
                    run_id,
                )
                for tool_call in tool_calls
            ]

            # Calling result() in submission order preserves
            # deterministic result ordering.
            return [
                future.result()
                for future in futures
            ]
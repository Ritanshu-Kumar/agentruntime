import time

from app.application.llm import ToolCall
from app.application.parallel.executor import ParallelToolExecutor
from app.application.tool_executor import ToolExecutor
from app.domain.tools.base import ToolResult
from app.domain.tools.registry import ToolRegistry


class SlowTool:
    name = "slow"
    permissions = frozenset()

    def validate_input(self, arguments: dict[str, int]) -> dict[str, int]:
        return arguments

    def execute(self, arguments: dict[str, int]) -> ToolResult:
        time.sleep(0.1)
        return ToolResult.ok(arguments["value"])


def test_parallel_executor_runs_concurrently_and_preserves_input_order() -> None:
    registry = ToolRegistry()
    registry.register(SlowTool())
    parallel_executor = ParallelToolExecutor(
        ToolExecutor(registry, set()),
        max_workers=2,
    )
    tool_calls = [
        ToolCall(tool_name="slow", arguments={"value": 1}),
        ToolCall(tool_name="slow", arguments={"value": 2}),
    ]

    started = time.perf_counter()
    results = parallel_executor.execute(tool_calls)
    elapsed = time.perf_counter() - started

    assert [result.content for result in results] == ["1", "2"]
    assert all(result.success for result in results)
    assert elapsed < 0.18


def test_parallel_executor_returns_empty_for_no_calls() -> None:
    parallel_executor = ParallelToolExecutor(
        ToolExecutor(ToolRegistry(), set()),
    )

    assert parallel_executor.execute([]) == []

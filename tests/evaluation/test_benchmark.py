from app.application.agent import AgentRunner
from app.application.benchmark import BenchmarkRunner, BenchmarkSuite
from app.application.evaluation import EvaluationRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.tool_executor import ToolExecutor
from app.domain.evaluation.evaluator import EvaluationEvaluator
from app.domain.evaluation.models import BenchmarkTask
from app.domain.tools import Permission, ToolRegistry
from tests.support.tools import ExampleTool

def test_benchmark_runner_evaluates_multiple_tasks() -> None:
    agent = AgentRunner(
        llm=FakeLLM(
            responses=[
                FinalAnswer(content="first"),
                FinalAnswer(content="second"),
            ]
        ),
        tool_executor=make_executor(),
    )

    evaluation_runner = EvaluationRunner(
        agent=agent,
        evaluator=EvaluationEvaluator(),
    )

    suite = BenchmarkSuite(
        tasks=[
            BenchmarkTask(
                name="first",
                task="First task",
                expected_answer="first",
            ),
            BenchmarkTask(
                name="second",
                task="Second task",
                expected_answer="second",
            ),
        ]
    )

    runner = BenchmarkRunner(evaluation_runner)

    results, metrics = runner.run(suite)

    assert len(results) == 2
    assert all(result.success for result in results)
    assert metrics.total_tasks == 2
    assert metrics.successful_tasks == 2
    assert metrics.success_rate == 1.0

def make_executor() -> ToolExecutor:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    return ToolExecutor(
        registry,
        {Permission.FILESYSTEM_READ.value},
    )
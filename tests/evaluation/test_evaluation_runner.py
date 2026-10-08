from app.application.agent import AgentRunner
from app.application.evaluation import EvaluationRunner
from app.application.llm import FakeLLM, FinalAnswer, ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.evaluation.evaluator import EvaluationEvaluator
from app.domain.evaluation.models import BenchmarkTask
from app.domain.tools import Permission, ToolRegistry

from tests.support.tools import ExampleTool


def make_executor() -> ToolExecutor:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    return ToolExecutor(
        registry,
        {Permission.FILESYSTEM_READ.value},
    )


def test_evaluation_runner_evaluates_agent_run() -> None:
    agent = AgentRunner(
        llm=FakeLLM(
            responses=[
                ToolCall(
                    tool_name="example",
                    arguments={"value": 5},
                ),
                FinalAnswer(content="The result is 10."),
            ]
        ),
        tool_executor=make_executor(),
    )

    benchmark = BenchmarkTask(
        name="calculate",
        task="Calculate something.",
        expected_answer="The result is 10.",
        expected_tools=["example"],
        expected_tool_arguments=[{"value": 5}],
    )

    runner = EvaluationRunner(
        agent=agent,
        evaluator=EvaluationEvaluator(),
    )

    result = runner.run(benchmark)

    assert result.success is True
    assert result.answer_correct is True
    assert result.tools_correct is True
    assert result.actual_answer == "The result is 10."
    assert result.actual_tools == ["example"]
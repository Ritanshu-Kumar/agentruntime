from uuid import uuid4

from app.domain.evaluation.evaluator import EvaluationEvaluator
from app.domain.evaluation.models import BenchmarkTask


def test_evaluator_accepts_correct_answer_tools_and_arguments() -> None:
    benchmark = BenchmarkTask(
        name="calculate",
        task="Calculate something.",
        expected_answer="The result is 10.",
        expected_tools=["example"],
        expected_tool_arguments=[{"value": 5}],
    )

    result = EvaluationEvaluator().evaluate(
        benchmark=benchmark,
        run_id=uuid4(),
        actual_answer="The result is 10.",
        actual_tools=["example"],
        actual_tool_arguments=[{"value": 5}],
    )

    assert result.answer_correct is True
    assert result.tools_correct is True
    assert result.arguments_correct is True
    assert result.success is True


def test_evaluator_rejects_wrong_answer() -> None:
    benchmark = BenchmarkTask(
        name="calculate",
        task="Calculate something.",
        expected_answer="The result is 10.",
        expected_tools=["example"],
        expected_tool_arguments=[{"value": 5}],
    )

    result = EvaluationEvaluator().evaluate(
        benchmark=benchmark,
        run_id=uuid4(),
        actual_answer="The result is 20.",
        actual_tools=["example"],
        actual_tool_arguments=[{"value": 5}],
    )

    assert result.answer_correct is False
    assert result.tools_correct is True
    assert result.arguments_correct is True
    assert result.success is False


def test_evaluator_rejects_wrong_tool() -> None:
    benchmark = BenchmarkTask(
        name="calculate",
        task="Calculate something.",
        expected_answer="The result is 10.",
        expected_tools=["example"],
        expected_tool_arguments=[{"value": 5}],
    )

    result = EvaluationEvaluator().evaluate(
        benchmark=benchmark,
        run_id=uuid4(),
        actual_answer="The result is 10.",
        actual_tools=["wrong_tool"],
        actual_tool_arguments=[{"value": 5}],
    )

    assert result.answer_correct is True
    assert result.tools_correct is False
    assert result.arguments_correct is True
    assert result.success is False


def test_evaluator_rejects_wrong_tool_arguments() -> None:
    benchmark = BenchmarkTask(
        name="calculate",
        task="Calculate something.",
        expected_answer="The result is 10.",
        expected_tools=["example"],
        expected_tool_arguments=[{"value": 5}],
    )

    result = EvaluationEvaluator().evaluate(
        benchmark=benchmark,
        run_id=uuid4(),
        actual_answer="The result is 10.",
        actual_tools=["example"],
        actual_tool_arguments=[{"value": 10}],
    )

    assert result.answer_correct is True
    assert result.tools_correct is True
    assert result.arguments_correct is False
    assert result.success is False
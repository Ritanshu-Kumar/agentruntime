from uuid import uuid4

from app.domain.evaluation.metrics import EvaluationMetrics
from app.domain.evaluation.models import EvaluationResult


def make_result(
    *,
    answer_correct: bool,
    tools_correct: bool,
) -> EvaluationResult:
    return EvaluationResult(
        benchmark_name="test",
        run_id=uuid4(),
        actual_answer="answer",
        answer_correct=answer_correct,
        expected_tools=[],
        actual_tools=[],
        tools_correct=tools_correct,
        expected_tool_arguments=[],
        actual_tool_arguments=[],
        arguments_correct=True,
        success=answer_correct and tools_correct,
    )


def test_metrics_calculate_aggregate_results() -> None:
    results = [
        make_result(answer_correct=True, tools_correct=True),
        make_result(answer_correct=True, tools_correct=False),
        make_result(answer_correct=False, tools_correct=True),
        make_result(answer_correct=True, tools_correct=True),
    ]

    metrics = EvaluationMetrics.from_results(results)

    assert metrics.total_tasks == 4
    assert metrics.successful_tasks == 2
    assert metrics.answer_accuracy == 0.75
    assert metrics.tool_accuracy == 0.75
    assert metrics.success_rate == 0.5


def test_metrics_handle_empty_results() -> None:
    metrics = EvaluationMetrics.from_results([])

    assert metrics.total_tasks == 0
    assert metrics.successful_tasks == 0
    assert metrics.answer_accuracy == 0.0
    assert metrics.tool_accuracy == 0.0
    assert metrics.success_rate == 0.0
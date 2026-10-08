from uuid import UUID

from app.domain.evaluation.models import BenchmarkTask, EvaluationResult


class EvaluationEvaluator:
    def evaluate(
        self,
        benchmark: BenchmarkTask,
        run_id: UUID,
        actual_answer: str,
        actual_tools: list[str],
        actual_tool_arguments: list[dict],
    ) -> EvaluationResult:
        answer_correct = actual_answer == benchmark.expected_answer
        tools_correct = actual_tools == benchmark.expected_tools
        arguments_correct = (
            actual_tool_arguments
            == benchmark.expected_tool_arguments
        )

        return EvaluationResult(
            benchmark_name=benchmark.name,
            run_id=run_id,
            actual_answer=actual_answer,
            answer_correct=answer_correct,
            expected_tools=benchmark.expected_tools,
            actual_tools=actual_tools,
            tools_correct=tools_correct,
            expected_tool_arguments=benchmark.expected_tool_arguments,
            actual_tool_arguments=actual_tool_arguments,
            arguments_correct=arguments_correct,
            success=(
                answer_correct
                and tools_correct
                and arguments_correct
            ),
        )
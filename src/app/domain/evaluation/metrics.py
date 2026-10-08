from pydantic import BaseModel

from app.domain.evaluation.models import EvaluationResult


class EvaluationMetrics(BaseModel):
    total_tasks: int
    successful_tasks: int
    answer_accuracy: float
    tool_accuracy: float
    success_rate: float

    @classmethod
    def from_results(
        cls,
        results: list[EvaluationResult],
    ) -> "EvaluationMetrics":
        total = len(results)

        if total == 0:
            return cls(
                total_tasks=0,
                successful_tasks=0,
                answer_accuracy=0.0,
                tool_accuracy=0.0,
                success_rate=0.0,
            )

        successful = sum(result.success for result in results)
        answer_correct = sum(
            result.answer_correct for result in results
        )
        tools_correct = sum(
            result.tools_correct for result in results
        )

        return cls(
            total_tasks=total,
            successful_tasks=successful,
            answer_accuracy=answer_correct / total,
            tool_accuracy=tools_correct / total,
            success_rate=successful / total,
        )
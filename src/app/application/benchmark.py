from app.application.evaluation import EvaluationRunner
from app.domain.evaluation.metrics import EvaluationMetrics
from app.domain.evaluation.models import BenchmarkTask, EvaluationResult


class BenchmarkSuite:
    def __init__(
        self,
        tasks: list[BenchmarkTask],
    ) -> None:
        self.tasks = tasks


class BenchmarkRunner:
    def __init__(
        self,
        evaluation_runner: EvaluationRunner,
    ) -> None:
        self.evaluation_runner = evaluation_runner

    def run(
        self,
        suite: BenchmarkSuite,
    ) -> tuple[list[EvaluationResult], EvaluationMetrics]:
        results = [
            self.evaluation_runner.run(task)
            for task in suite.tasks
        ]

        metrics = EvaluationMetrics.from_results(results)

        return results, metrics
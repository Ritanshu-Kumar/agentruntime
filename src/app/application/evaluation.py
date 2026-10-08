from app.application.agent import AgentRunner
from app.domain.evaluation.evaluator import EvaluationEvaluator
from app.domain.evaluation.models import BenchmarkTask, EvaluationResult


class EvaluationRunner:
    def __init__(
        self,
        agent: AgentRunner,
        evaluator: EvaluationEvaluator,
    ) -> None:
        self.agent = agent
        self.evaluator = evaluator

    def run(self, benchmark: BenchmarkTask) -> EvaluationResult:
        result = self.agent.run(benchmark.task)

        run_id = self.agent.last_run_id

        return self.evaluator.evaluate(
            benchmark=benchmark,
            run_id=run_id,
            actual_answer=result,
            actual_tools=self.agent.last_tool_calls,
            actual_tool_arguments=self.agent.last_tool_arguments,
        )
from datetime import datetime

from app.application.agent import AgentRunner
from app.domain.scheduling.repository import ScheduleRepository


class Scheduler:
    def __init__(
        self,
        repository: ScheduleRepository,
        agent: AgentRunner,
    ) -> None:
        self.repository = repository
        self.agent = agent

    def run_due(self, now: datetime) -> list[str]:
        results = []
        for scheduled_run in self.repository.due(now):
            result = self.agent.run(scheduled_run.task)
            self.repository.mark_completed(scheduled_run.id)
            results.append(result)
        return results

from datetime import datetime
from uuid import UUID

from app.domain.scheduling.models import ScheduledRun
from app.domain.scheduling.repository import ScheduleRepository


class InMemoryScheduleRepository(ScheduleRepository):
    def __init__(self) -> None:
        self._runs: dict[UUID, ScheduledRun] = {}

    def create(
        self,
        scheduled_run: ScheduledRun,
    ) -> ScheduledRun:
        self._runs[scheduled_run.id] = scheduled_run
        return scheduled_run

    def due(self, now: datetime) -> list[ScheduledRun]:
        return [
            run
            for run in self._runs.values()
            if not run.completed
            and run.run_at <= now
        ]

    def mark_completed(self, run_id: UUID) -> None:
        run = self._runs[run_id]
        run.completed = True
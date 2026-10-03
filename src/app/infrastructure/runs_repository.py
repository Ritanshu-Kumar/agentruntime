from uuid import UUID

from app.domain.observability.events import ExecutionEvent
from app.domain.runs.models import Run
from app.domain.runs.repository import RunRepository


class InMemoryRunRepository(RunRepository):
    def __init__(self) -> None:
        self._runs: dict[UUID, Run] = {}
        self._execution_events: dict[UUID, list[ExecutionEvent]] = {}

    def create(self, run: Run) -> Run:
        if run.id in self._runs:
            raise ValueError(f"Run already exists: {run.id}")

        self._runs[run.id] = run
        self._execution_events.setdefault(run.id, [])
        return run

    def get(self, run_id: UUID) -> Run | None:
        return self._runs.get(run_id)

    def save(self, run: Run) -> Run:
        if run.id not in self._runs:
            raise ValueError(f"Run does not exist: {run.id}")

        self._runs[run.id] = run
        self._execution_events.setdefault(run.id, [])
        return run

    def save_execution_events(
        self,
        run_id: UUID,
        events: list[ExecutionEvent],
    ) -> list[ExecutionEvent]:
        self._execution_events[run_id] = list(events)
        return list(events)

    def get_execution_events(self, run_id: UUID) -> list[ExecutionEvent]:
        return list(self._execution_events.get(run_id, []))
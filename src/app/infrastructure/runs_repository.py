from uuid import UUID

from app.domain.runs.models import Run
from app.domain.runs.repository import RunRepository


class InMemoryRunRepository(RunRepository):
    def __init__(self) -> None:
        self._runs: dict[UUID, Run] = {}

    def create(self, run: Run) -> Run:
        if run.id in self._runs:
            raise ValueError(f"Run already exists: {run.id}")

        self._runs[run.id] = run
        return run

    def get(self, run_id: UUID) -> Run | None:
        return self._runs.get(run_id)

    def save(self, run: Run) -> Run:
        if run.id not in self._runs:
            raise ValueError(f"Run does not exist: {run.id}")

        self._runs[run.id] = run
        return run
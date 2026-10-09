from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.observability.events import ExecutionEvent
from app.domain.runs.models import Run


class RunRepository(ABC):
    @abstractmethod
    def create(self, run: Run) -> Run:
        raise NotImplementedError

    @abstractmethod
    def get(self, run_id: UUID) -> Run | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, run: Run) -> Run:
        raise NotImplementedError

    def save_execution_events(
        self,
        run_id: UUID,
        events: list[ExecutionEvent],
    ) -> list[ExecutionEvent]:
        return list(events)

    def get_execution_events(self, run_id: UUID) -> list[ExecutionEvent]:
        return []

    def list_runs(self, limit: int = 20) -> list[Run]:
        return []

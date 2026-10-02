from abc import ABC, abstractmethod
from uuid import UUID

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
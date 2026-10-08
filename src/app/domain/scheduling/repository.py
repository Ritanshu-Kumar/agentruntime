from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.scheduling.models import ScheduledRun


class ScheduleRepository(ABC):

    @abstractmethod
    def create(
        self,
        scheduled_run: ScheduledRun,
    ) -> ScheduledRun:
        raise NotImplementedError

    @abstractmethod
    def due(
        self,
        now: datetime,
    ) -> list[ScheduledRun]:
        raise NotImplementedError

    @abstractmethod
    def mark_completed(
        self,
        run_id: UUID,
    ) -> None:
        raise NotImplementedError
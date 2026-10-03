from uuid import UUID

from app.domain.observability.events import EventType, ExecutionEvent


class EventRecorder:
    def __init__(self) -> None:
        self._events: list[ExecutionEvent] = []

    def record(
        self,
        run_id: UUID,
        event_type: EventType,
        metadata: dict | None = None,
    ) -> ExecutionEvent:
        event = ExecutionEvent(
            run_id=run_id,
            event_type=event_type,
            metadata=metadata or {},
        )

        self._events.append(event)
        return event

    def events(self, run_id: UUID) -> list[ExecutionEvent]:
        return [
            event
            for event in self._events
            if event.run_id == run_id
        ]

    def all_events(self) -> list[ExecutionEvent]:
        return list(self._events)
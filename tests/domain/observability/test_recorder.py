from uuid import uuid4

from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder


def test_records_event() -> None:
    recorder = EventRecorder()
    run_id = uuid4()

    event = recorder.record(
        run_id,
        EventType.RUN_STARTED,
    )

    assert event.run_id == run_id
    assert recorder.events(run_id) == [event]


def test_records_events_in_order() -> None:
    recorder = EventRecorder()
    run_id = uuid4()

    first = recorder.record(
        run_id,
        EventType.RUN_STARTED,
    )
    second = recorder.record(
        run_id,
        EventType.MODEL_CALLED,
    )

    assert recorder.events(run_id) == [first, second]


def test_filters_events_by_run() -> None:
    recorder = EventRecorder()
    first_run = uuid4()
    second_run = uuid4()

    first_event = recorder.record(
        first_run,
        EventType.RUN_STARTED,
    )
    recorder.record(
        second_run,
        EventType.RUN_STARTED,
    )

    assert recorder.events(first_run) == [first_event]


def test_all_events_returns_all_events() -> None:
    recorder = EventRecorder()
    first_run = uuid4()
    second_run = uuid4()

    recorder.record(first_run, EventType.RUN_STARTED)
    recorder.record(second_run, EventType.RUN_STARTED)

    assert len(recorder.all_events()) == 2
from uuid import uuid4

from app.domain.observability.events import EventType, ExecutionEvent


def test_execution_event_defaults() -> None:
    run_id = uuid4()

    event = ExecutionEvent(
        run_id=run_id,
        event_type=EventType.RUN_STARTED,
    )

    assert event.run_id == run_id
    assert event.event_type == EventType.RUN_STARTED
    assert event.timestamp is not None
    assert event.metadata == {}
    assert event.id is not None


def test_execution_event_metadata() -> None:
    run_id = uuid4()

    event = ExecutionEvent(
        run_id=run_id,
        event_type=EventType.TOOL_CALLED,
        metadata={
            "tool_name": "execute_python",
        },
    )

    assert event.metadata["tool_name"] == "execute_python"


def test_event_types() -> None:
    assert EventType.RUN_STARTED == "run.started"
    assert EventType.MODEL_CALLED == "model.called"
    assert EventType.TOOL_CALLED == "tool.called"
    assert EventType.TOOL_COMPLETED == "tool.completed"
    assert EventType.RETRY == "retry"
    assert EventType.RUN_COMPLETED == "run.completed"
    assert EventType.RUN_FAILED == "run.failed"
    assert EventType.TOOL_BLOCKED == "tool.blocked"
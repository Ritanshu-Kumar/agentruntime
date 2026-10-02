from datetime import timezone

from app.application.messages import (
    ToolMessage,
    UserMessage,
)
from app.domain.runs import Run, RunStatus


def test_run_defaults() -> None:
    run = Run(task="Read README.md")

    assert run.status == RunStatus.PENDING
    assert run.messages == []
    assert run.id is not None
    assert run.created_at.tzinfo == timezone.utc
    assert run.updated_at.tzinfo == timezone.utc


def test_run_contains_messages() -> None:
    run = Run(task="Read README.md")

    run.messages.append(
        UserMessage(content="Read README.md")
    )

    run.messages.append(
        ToolMessage(
            tool_name="read_file",
            success=True,
            content="hello",
        )
    )

    assert len(run.messages) == 2
    assert run.messages[0].content == "Read README.md"
    assert run.messages[1].tool_name == "read_file"


def test_run_status_can_change() -> None:
    run = Run(task="Test")

    run.status = RunStatus.RUNNING

    assert run.status == RunStatus.RUNNING


def test_run_serializes() -> None:
    run = Run(task="Test")

    data = run.model_dump(mode="json")

    assert data["task"] == "Test"
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(StrEnum):
    RUN_STARTED = "run.started"
    MODEL_CALLED = "model.called"
    TOOL_CALLED = "tool.called"
    TOOL_COMPLETED = "tool.completed"
    RETRY = "retry"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"


class ExecutionEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    event_type: EventType
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
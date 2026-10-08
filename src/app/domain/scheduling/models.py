from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ScheduledRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task: str
    run_at: datetime
    completed: bool = False
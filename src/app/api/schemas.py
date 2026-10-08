from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.runs.models import RunStatus


class CreateRunRequest(BaseModel):
    task: str = Field(min_length=1)


class RunResponse(BaseModel):
    id: UUID
    task: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    answer: str | None = None


class ErrorResponse(BaseModel):
    detail: str


class ResumeRunRequest(BaseModel):
    approval_id: UUID
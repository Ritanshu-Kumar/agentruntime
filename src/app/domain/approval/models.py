from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"


class ApprovalRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    tool_name: str
    arguments: dict[str, Any]
    reason: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    decided_at: datetime | None = None
    decision: ApprovalDecision | None = None
    decision_reason: str | None = None

    def approve(self, reason: str | None = None) -> None:
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Approval request is no longer pending")

        self.status = ApprovalStatus.APPROVED
        self.decision = ApprovalDecision.APPROVE
        self.decision_reason = reason
        self.decided_at = datetime.now(timezone.utc)

    def reject(self, reason: str | None = None) -> None:
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Approval request is no longer pending")

        self.status = ApprovalStatus.REJECTED
        self.decision = ApprovalDecision.REJECT
        self.decision_reason = reason
        self.decided_at = datetime.now(timezone.utc)
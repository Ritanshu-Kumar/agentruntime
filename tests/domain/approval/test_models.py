from uuid import uuid4

import pytest

from app.domain.approval.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
)


def test_approval_starts_pending():
    request = ApprovalRequest(
        run_id=uuid4(),
        tool_name="sensitive_tool",
        arguments={"value": "x"},
        reason="Requires human approval",
    )

    assert request.status == ApprovalStatus.PENDING
    assert request.decision is None
    assert request.decided_at is None


def test_approval_can_be_granted():
    request = ApprovalRequest(
        run_id=uuid4(),
        tool_name="sensitive_tool",
        arguments={},
        reason="Requires human approval",
    )

    request.approve("Approved by operator")

    assert request.status == ApprovalStatus.APPROVED
    assert request.decision == ApprovalDecision.APPROVE
    assert request.decision_reason == "Approved by operator"
    assert request.decided_at is not None


def test_approval_can_be_rejected():
    request = ApprovalRequest(
        run_id=uuid4(),
        tool_name="sensitive_tool",
        arguments={},
        reason="Requires human approval",
    )

    request.reject("Not authorized")

    assert request.status == ApprovalStatus.REJECTED
    assert request.decision == ApprovalDecision.REJECT
    assert request.decision_reason == "Not authorized"
    assert request.decided_at is not None


def test_cannot_decide_twice():
    request = ApprovalRequest(
        run_id=uuid4(),
        tool_name="sensitive_tool",
        arguments={},
        reason="Requires human approval",
    )

    request.approve()

    with pytest.raises(ValueError):
        request.reject()
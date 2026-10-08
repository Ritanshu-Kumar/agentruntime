from uuid import uuid4

from app.domain.approval.models import ApprovalStatus
from app.domain.approval.repository import InMemoryApprovalRepository
from app.domain.approval.models import ApprovalRequest


def test_repository_stores_request():
    repository = InMemoryApprovalRepository()

    request = ApprovalRequest(
        run_id=uuid4(),
        tool_name="sensitive_tool",
        arguments={"x": 1},
        reason="Requires approval",
    )

    repository.create(request)

    assert repository.get(request.id) == request


def test_repository_returns_pending_requests_for_run():
    repository = InMemoryApprovalRepository()
    run_id = uuid4()

    request = ApprovalRequest(
        run_id=run_id,
        tool_name="sensitive_tool",
        arguments={},
        reason="Requires approval",
    )

    repository.create(request)

    pending = repository.get_pending_for_run(run_id)

    assert len(pending) == 1
    assert pending[0].status == ApprovalStatus.PENDING
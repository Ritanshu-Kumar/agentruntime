from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.approval.models import ApprovalRequest, ApprovalStatus


class ApprovalRepository(ABC):
    @abstractmethod
    def create(self, request: ApprovalRequest) -> ApprovalRequest:
        raise NotImplementedError

    @abstractmethod
    def get(self, approval_id: UUID) -> ApprovalRequest | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, request: ApprovalRequest) -> ApprovalRequest:
        raise NotImplementedError

    @abstractmethod
    def get_pending_for_run(
        self,
        run_id: UUID,
    ) -> list[ApprovalRequest]:
        raise NotImplementedError


class InMemoryApprovalRepository(ApprovalRepository):
    def __init__(self) -> None:
        self._requests: dict[UUID, ApprovalRequest] = {}

    def create(self, request: ApprovalRequest) -> ApprovalRequest:
        self._requests[request.id] = request
        return request

    def get(self, approval_id: UUID) -> ApprovalRequest | None:
        return self._requests.get(approval_id)

    def save(self, request: ApprovalRequest) -> ApprovalRequest:
        self._requests[request.id] = request
        return request

    def get_pending_for_run(
        self,
        run_id: UUID,
    ) -> list[ApprovalRequest]:
        return [
            request
            for request in self._requests.values()
            if request.run_id == run_id
            and request.status == ApprovalStatus.PENDING
        ]
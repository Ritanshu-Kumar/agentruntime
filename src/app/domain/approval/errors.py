from app.domain.approval.models import ApprovalRequest


class ApprovalRequiredError(Exception):
    def __init__(self, request: ApprovalRequest) -> None:
        self.request = request

        super().__init__(
            f"Approval required for tool '{request.tool_name}'"
        )
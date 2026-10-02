from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.application.messages import (
    AssistantMessage,
    ToolMessage,
    UserMessage,
)
from app.domain.runs import Run
from app.domain.runs.repository import RunRepository
from app.infrastructure.db.message_models import MessageRecord
from app.infrastructure.db.models import RunRecord


class PostgresRunRepository(RunRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, run: Run) -> Run:
        record = RunRecord(
            id=str(run.id),
            task=run.task,
            status=run.status,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )

        self.session.add(record)
        self._save_messages(run)

        self.session.commit()

        return run

    def get(self, run_id: UUID) -> Run | None:
        record = self.session.get(RunRecord, str(run_id))

        if record is None:
            return None

        messages = self._load_messages(str(run_id))

        return Run(
            id=UUID(record.id),
            task=record.task,
            status=record.status,
            messages=messages,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def save(self, run: Run) -> Run:
        record = self.session.get(RunRecord, str(run.id))

        if record is None:
            raise ValueError(f"Run does not exist: {run.id}")

        record.task = run.task
        record.status = run.status
        record.updated_at = run.updated_at

        self.session.execute(
            delete(MessageRecord).where(
                MessageRecord.run_id == str(run.id)
            )
        )

        self._save_messages(run)

        self.session.commit()

        return run

    def _save_messages(self, run: Run) -> None:
        for message in run.messages:
            if isinstance(message, UserMessage):
                record = MessageRecord(
                    run_id=str(run.id),
                    role="user",
                    content=message.content,
                )
            elif isinstance(message, AssistantMessage):
                record = MessageRecord(
                    run_id=str(run.id),
                    role="assistant",
                    content=message.content,
                )
            elif isinstance(message, ToolMessage):
                record = MessageRecord(
                    run_id=str(run.id),
                    role="tool",
                    content=message.content,
                    tool_name=message.tool_name,
                    success=message.success,
                )
            else:
                raise TypeError(
                    f"Unsupported message type: {type(message)}"
                )

            self.session.add(record)

    def _load_messages(
        self,
        run_id: str,
    ) -> list:
        records = (
            self.session.query(MessageRecord)
            .filter(MessageRecord.run_id == run_id)
            .order_by(MessageRecord.id)
            .all()
        )

        messages = []

        for record in records:
            if record.role == "user":
                messages.append(
                    UserMessage(content=record.content)
                )
            elif record.role == "assistant":
                messages.append(
                    AssistantMessage(content=record.content)
                )
            elif record.role == "tool":
                messages.append(
                    ToolMessage(
                        tool_name=record.tool_name or "",
                        success=record.success or False,
                        content=record.content,
                    )
                )

        return messages
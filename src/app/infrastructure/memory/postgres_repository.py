import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.domain.memory.models import Memory
from app.domain.memory.repository import MemoryStore
from app.infrastructure.memory.models import MemoryRecord


class PostgresMemoryStore(MemoryStore):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, memory: Memory) -> Memory:
        record = self.session.scalar(
            select(MemoryRecord).where(
                MemoryRecord.namespace == memory.namespace,
                MemoryRecord.key == memory.key,
            )
        )

        if record is None:
            record = MemoryRecord(
                id=str(memory.id),
                namespace=memory.namespace,
                key=memory.key,
                value=memory.value,
                created_at=memory.created_at,
                updated_at=memory.updated_at,
            )
            self.session.add(record)
        else:
            record.value = memory.value
            record.updated_at = datetime.now(timezone.utc)

        self.session.commit()
        return self._to_memory(record)

    def get(
        self,
        namespace: str,
        key: str,
    ) -> Memory | None:
        record = self.session.scalar(
            select(MemoryRecord).where(
                MemoryRecord.namespace == namespace,
                MemoryRecord.key == key,
            )
        )
        return self._to_memory(record) if record is not None else None

    def delete(
        self,
        namespace: str,
        key: str,
    ) -> None:
        self.session.execute(
            delete(MemoryRecord).where(
                MemoryRecord.namespace == namespace,
                MemoryRecord.key == key,
            )
        )
        self.session.commit()

    def search(
        self,
        namespace: str,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        query_words = {
            word
            for word in re.findall(r"[a-z0-9]+", query.lower())
        }
        if not query_words or limit <= 0:
            return []

        records = self.session.scalars(
            select(MemoryRecord)
            .where(MemoryRecord.namespace == namespace)
            .order_by(MemoryRecord.created_at, MemoryRecord.key)
        ).all()

        ranked: list[tuple[int, Memory]] = []
        for record in records:
            memory = self._to_memory(record)
            memory_words = {
                word
                for word in re.findall(
                    r"[a-z0-9]+",
                    f"{memory.key} {memory.value}".lower(),
                )
            }
            score = len(query_words & memory_words)
            if score:
                ranked.append((score, memory))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in ranked[:limit]]

    @staticmethod
    def _to_memory(record: MemoryRecord) -> Memory:
        return Memory(
            id=UUID(record.id),
            namespace=record.namespace,
            key=record.key,
            value=record.value,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

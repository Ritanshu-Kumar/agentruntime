from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Memory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    namespace: str
    key: str
    value: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update(self, value: str) -> None:
        self.value = value
        self.updated_at = datetime.now(timezone.utc)

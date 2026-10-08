from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.domain.memory.models import Memory
from app.infrastructure.db.models import Base
from app.infrastructure.memory.models import MemoryRecord
from app.infrastructure.memory.postgres_repository import PostgresMemoryStore


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_memory_record_is_registered_with_existing_metadata() -> None:
    assert "memories" in Base.metadata.tables
    assert MemoryRecord.__tablename__ == "memories"


def test_postgres_memory_store_save_get_update_delete_and_search() -> None:
    store = PostgresMemoryStore(create_session())
    memory = Memory(
        namespace="user-1",
        key="preferred_language",
        value="Python",
    )

    stored = store.save(memory)
    found = store.get("user-1", "preferred_language")

    assert found is not None
    assert found.id == memory.id
    assert found.value == "Python"
    assert store.search("user-1", "What language do I prefer?")[0].key == (
        "preferred_language"
    )
    assert store.search("user-2", "Python") == []

    updated = store.save(
        Memory(
            namespace="user-1",
            key="preferred_language",
            value="Rust",
        )
    )

    assert updated.id == stored.id
    assert updated.value == "Rust"
    assert updated.created_at == stored.created_at
    assert updated.updated_at >= stored.updated_at

    store.delete("user-1", "preferred_language")
    assert store.get("user-1", "preferred_language") is None


def test_postgres_memory_store_preserves_timestamps_on_insert() -> None:
    created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    updated_at = datetime(2024, 1, 2, tzinfo=timezone.utc)
    store = PostgresMemoryStore(create_session())

    stored = store.save(
        Memory(
            namespace="user-1",
            key="fact",
            value="remembered",
            created_at=created_at,
            updated_at=updated_at,
        )
    )

    assert stored.created_at.replace(tzinfo=timezone.utc) == created_at
    assert stored.updated_at.replace(tzinfo=timezone.utc) == updated_at

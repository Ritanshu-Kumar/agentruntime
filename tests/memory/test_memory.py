from app.application.memory import MemoryService
from app.domain.memory.context import format_memory_context
from app.domain.memory.in_memory import InMemoryMemoryStore
from app.domain.memory.models import Memory


def test_memory_can_be_saved_and_retrieved() -> None:
    store = InMemoryMemoryStore()
    memory = Memory(
        namespace="user-1",
        key="favorite_language",
        value="Python",
    )

    store.save(memory)

    result = store.get("user-1", "favorite_language")
    assert result is not None
    assert result.value == "Python"


def test_memory_isolated_by_namespace() -> None:
    store = InMemoryMemoryStore()
    store.save(
        Memory(
            namespace="user-1",
            key="language",
            value="Python",
        )
    )

    assert store.get("user-2", "language") is None
    assert store.search("user-2", "Python") == []


def test_memory_save_updates_existing_value() -> None:
    store = InMemoryMemoryStore()
    original = store.save(
        Memory(
            namespace="user-1",
            key="language",
            value="Python",
        )
    )

    updated = store.save(
        Memory(
            namespace="user-1",
            key="language",
            value="Rust",
        )
    )

    assert updated.id == original.id
    assert updated.value == "Rust"


def test_memory_search_ranks_keyword_matches_and_limits_results() -> None:
    store = InMemoryMemoryStore()
    store.save(
        Memory(
            namespace="user-1",
            key="preferred_language",
            value="Python",
        )
    )
    store.save(
        Memory(
            namespace="user-1",
            key="editor",
            value="VS Code",
        )
    )

    result = store.search(
        "user-1",
        "What programming language do I prefer?",
        limit=1,
    )

    assert len(result) == 1
    assert result[0].key == "preferred_language"


def test_memory_search_returns_empty_for_no_keywords_or_nonpositive_limit() -> None:
    store = InMemoryMemoryStore()
    store.save(
        Memory(
            namespace="user-1",
            key="language",
            value="Python",
        )
    )

    assert store.search("user-1", "   ") == []
    assert store.search("user-1", "Python", limit=0) == []


def test_memory_delete() -> None:
    store = InMemoryMemoryStore()
    store.save(
        Memory(
            namespace="user-1",
            key="language",
            value="Python",
        )
    )

    store.delete("user-1", "language")

    assert store.get("user-1", "language") is None


def test_format_memory_context() -> None:
    context = format_memory_context(
        [
            Memory(
                namespace="user-1",
                key="preferred_language",
                value="Python",
            )
        ]
    )

    assert context == "Relevant memory:\n- preferred_language: Python"
    assert format_memory_context([]) == ""


def test_memory_service_remembers_and_recalls() -> None:
    service = MemoryService(InMemoryMemoryStore())

    stored = service.remember("user-1", "language", "Python")
    recalled = service.recall("user-1", "language")

    assert recalled == stored

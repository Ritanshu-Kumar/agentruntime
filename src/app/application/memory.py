from app.domain.memory.models import Memory
from app.domain.memory.repository import MemoryStore


class MemoryService:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def remember(
        self,
        namespace: str,
        key: str,
        value: str,
    ) -> Memory:
        memory = Memory(
            namespace=namespace,
            key=key,
            value=value,
        )
        return self.store.save(memory)

    def recall(
        self,
        namespace: str,
        key: str,
    ) -> Memory | None:
        return self.store.get(namespace, key)

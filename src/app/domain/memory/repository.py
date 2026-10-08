from abc import ABC, abstractmethod

from app.domain.memory.models import Memory


class MemoryStore(ABC):
    @abstractmethod
    def save(self, memory: Memory) -> Memory:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        namespace: str,
        key: str,
    ) -> Memory | None:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        namespace: str,
        key: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        namespace: str,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        raise NotImplementedError

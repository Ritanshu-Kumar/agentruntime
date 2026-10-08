import re

from app.domain.memory.models import Memory
from app.domain.memory.repository import MemoryStore


class InMemoryMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._memories: dict[tuple[str, str], Memory] = {}

    def save(self, memory: Memory) -> Memory:
        key = (memory.namespace, memory.key)
        existing = self._memories.get(key)
        if existing is not None:
            existing.update(memory.value)
            return existing
        self._memories[key] = memory
        return memory

    def get(
        self,
        namespace: str,
        key: str,
    ) -> Memory | None:
        return self._memories.get((namespace, key))

    def delete(
        self,
        namespace: str,
        key: str,
    ) -> None:
        self._memories.pop((namespace, key), None)

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

        ranked: list[tuple[int, Memory]] = []
        for memory in self._memories.values():
            if memory.namespace != namespace:
                continue

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

from abc import ABC, abstractmethod

from app.application.llm import LLMClient


class ModelRouter(ABC):
    """Selects an LLM for an agent request."""

    @abstractmethod
    def select(
        self,
        messages: list[dict[str, str]],
    ) -> LLMClient:
        raise NotImplementedError


class StaticModelRouter(ModelRouter):
    """Always routes requests to the same model."""

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def select(
        self,
        messages: list[dict[str, str]],
    ) -> LLMClient:
        return self.client


class KeywordModelRouter(ModelRouter):
    """
    Simple educational router.

    Requests containing configured keywords are sent to the
    specialized client; everything else uses the default client.
    """

    def __init__(
        self,
        default_client: LLMClient,
        specialized_client: LLMClient,
        keywords: set[str],
    ) -> None:
        self.default_client = default_client
        self.specialized_client = specialized_client
        self.keywords = {
            keyword.lower()
            for keyword in keywords
        }

    def select(
        self,
        messages: list[dict[str, str]],
    ) -> LLMClient:
        text = " ".join(
            message.get("content", "")
            for message in messages
        ).lower()

        if any(keyword in text for keyword in self.keywords):
            return self.specialized_client

        return self.default_client
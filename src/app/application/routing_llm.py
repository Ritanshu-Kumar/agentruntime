from app.application.llm import LLMClient, LLMResponse
from app.domain.routing.router import ModelRouter


class RoutingLLMClient(LLMClient):
    """
    LLMClient facade that delegates each request to a selected model.
    """

    def __init__(self, router: ModelRouter) -> None:
        self.router = router
        self.selected_models: list[LLMClient] = []

    def respond(
        self,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        client = self.router.select(messages)
        self.selected_models.append(client)
        return client.respond(messages)
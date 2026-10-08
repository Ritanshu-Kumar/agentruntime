from app.application.llm import FinalAnswer, FakeLLM
from app.application.routing_llm import RoutingLLMClient
from app.domain.routing.router import (
    KeywordModelRouter,
    StaticModelRouter,
)


def test_static_router_returns_configured_client():
    client = FakeLLM(
        [FinalAnswer(content="hello")]
    )

    router = StaticModelRouter(client)

    assert router.select([]) is client


def test_keyword_router_selects_specialized_model():
    default = FakeLLM(
        [FinalAnswer(content="default")]
    )
    specialized = FakeLLM(
        [FinalAnswer(content="specialized")]
    )

    router = KeywordModelRouter(
        default_client=default,
        specialized_client=specialized,
        keywords={"python", "code"},
    )

    selected = router.select(
        [
            {
                "role": "user",
                "content": "Write Python code",
            }
        ]
    )

    assert selected is specialized


def test_keyword_router_uses_default_model():
    default = FakeLLM(
        [FinalAnswer(content="default")]
    )
    specialized = FakeLLM(
        [FinalAnswer(content="specialized")]
    )

    router = KeywordModelRouter(
        default_client=default,
        specialized_client=specialized,
        keywords={"python", "code"},
    )

    selected = router.select(
        [
            {
                "role": "user",
                "content": "What is the capital of France?",
            }
        ]
    )

    assert selected is default


def test_routing_llm_client_delegates():
    default = FakeLLM(
        [FinalAnswer(content="default")]
    )
    specialized = FakeLLM(
        [FinalAnswer(content="specialized")]
    )

    router = KeywordModelRouter(
        default_client=default,
        specialized_client=specialized,
        keywords={"python"},
    )

    client = RoutingLLMClient(router)

    response = client.respond(
        [
            {
                "role": "user",
                "content": "Write Python code",
            }
        ]
    )

    assert isinstance(response, FinalAnswer)
    assert response.content == "specialized"
    assert client.selected_models == [specialized]
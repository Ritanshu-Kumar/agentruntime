from typing import Any

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.messages import SystemMessage
from app.application.tool_executor import ToolExecutor
from app.domain.memory.in_memory import InMemoryMemoryStore
from app.domain.memory.models import Memory
from app.domain.policy.models import AgentPolicy
from app.domain.tools.registry import ToolRegistry
from app.infrastructure.runs_repository import InMemoryRunRepository


class RecordingFakeLLM(FakeLLM):
    def __init__(self) -> None:
        super().__init__([FinalAnswer(content="Python is preferred.")])
        self.received_messages: list[list[dict[str, Any]]] = []

    def respond(self, messages: list[dict[str, Any]]) -> FinalAnswer:
        self.received_messages.append(messages)
        return super().respond(messages)


def test_agent_receives_relevant_memory_without_changing_task() -> None:
    memory_store = InMemoryMemoryStore()
    memory_store.save(
        Memory(
            namespace="user-1",
            key="preferred_language",
            value="Python",
        )
    )
    llm = RecordingFakeLLM()
    run_repository = InMemoryRunRepository()
    runner = AgentRunner(
        llm=llm,
        tool_executor=ToolExecutor(ToolRegistry(), set()),
        run_repository=run_repository,
        memory_store=memory_store,
        memory_namespace="user-1",
    )
    task = "What programming language do I prefer?"

    result = runner.run(task)

    run = run_repository.get(runner.last_run_id)
    assert run is not None
    assert result == "Python is preferred."
    assert llm.calls == 1
    assert run.task == task
    assert isinstance(run.messages[0], SystemMessage)
    assert run.messages[0].content == (
        "Relevant memory:\n- preferred_language: Python"
    )
    assert llm.received_messages[0][0] == {
        "role": "system",
        "content": "Relevant memory:\n- preferred_language: Python",
    }


def test_agent_policy_can_disable_memory_context() -> None:
    memory_store = InMemoryMemoryStore()
    memory_store.save(
        Memory(
            namespace="user-1",
            key="preferred_language",
            value="Python",
        )
    )
    llm = RecordingFakeLLM()
    runner = AgentRunner(
        llm=llm,
        tool_executor=ToolExecutor(ToolRegistry(), set()),
        memory_store=memory_store,
        memory_namespace="user-1",
        policy=AgentPolicy(allow_memory=False),
    )

    runner.run("What programming language do I prefer?")

    assert llm.received_messages[0] == [
        {
            "role": "user",
            "content": "What programming language do I prefer?",
        }
    ]

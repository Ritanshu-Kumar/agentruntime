from fastapi import Request

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.tool_executor import ToolExecutor
from app.domain.tools.registry import ToolRegistry
from app.infrastructure.runs_repository import InMemoryRunRepository
from app.application.llm import LLMClient, FinalAnswer
from app.domain.observability.recorder import EventRecorder


def _build_default_runner() -> AgentRunner:
    event_recorder = EventRecorder()

    return AgentRunner(
        llm=DefaultDevelopmentLLM(),
        tool_executor=ToolExecutor(
            registry=ToolRegistry(),
            permissions=set(),
        ),
        run_repository=InMemoryRunRepository(),
        event_recorder=event_recorder,
    )


def get_agent_runner(request: Request) -> AgentRunner:
    runner = getattr(
        request.app.state,
        "agent_runner",
        None,
    )

    if runner is None:
        runner = _build_default_runner()
        request.app.state.agent_runner = runner

    return runner

class DefaultDevelopmentLLM(LLMClient):

    def respond(self, messages: list[dict[str, str]]) -> FinalAnswer:
        return FinalAnswer(content="Default agent response")

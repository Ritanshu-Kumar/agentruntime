from fastapi import Request

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.tool_executor import ToolExecutor
from app.domain.tools.registry import ToolRegistry
from app.infrastructure.runs_repository import InMemoryRunRepository


def _build_default_runner() -> AgentRunner:
    return AgentRunner(
        llm=FakeLLM([FinalAnswer(content="Default agent response")]),
        tool_executor=ToolExecutor(
            registry=ToolRegistry(),
            permissions=set(),
        ),
        run_repository=InMemoryRunRepository(),
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
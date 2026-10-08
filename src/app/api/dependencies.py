from fastapi import Request

from app.application.agent import AgentRunner


def get_agent_runner(request: Request) -> AgentRunner:
    runner = getattr(
        request.app.state,
        "agent_runner",
        None,
    )

    if runner is None:
        raise RuntimeError(
            "AgentRunner has not been configured"
        )

    return runner
import logging

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.tool_executor import ToolExecutor
from app.domain.tools.registry import ToolRegistry


def test_agent_logs_run_start_and_completion(caplog) -> None:
    runner = AgentRunner(
        llm=FakeLLM([FinalAnswer(content="Done.")]),
        tool_executor=ToolExecutor(
            registry=ToolRegistry(),
            permissions=set(),
        ),
    )

    with caplog.at_level(
        logging.INFO,
        logger="app.application.agent",
    ):
        result = runner.run("Test task")

    assert result == "Done."

    records = [
        record
        for record in caplog.records
        if record.name == "app.application.agent"
    ]

    assert any(
        getattr(record, "event", None) == "run.started"
        for record in records
    )
    assert any(
        getattr(record, "event", None) == "model.called"
        for record in records
    )
    assert any(
        getattr(record, "event", None) == "run.completed"
        for record in records
    )

    assert all(
        getattr(record, "run_id", None) == str(runner.last_run_id)
        for record in records
    )

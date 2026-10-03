import pytest
from pydantic import BaseModel

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer, LLMUsage, ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.tools import Permission, Tool, ToolRegistry, ToolResult


class ExampleInput(BaseModel):
    value: int


class ExampleTool(Tool[ExampleInput]):
    name = "example"
    description = "Example tool"
    input_schema = ExampleInput
    permissions = frozenset({Permission.FILESYSTEM_READ})

    def execute(self, arguments: ExampleInput) -> ToolResult:
        return ToolResult.ok(arguments.value * 2)


def make_executor() -> ToolExecutor:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    return ToolExecutor(
        registry,
        {Permission.FILESYSTEM_READ.value},
    )


tool_executor = make_executor()


def test_agent_returns_final_answer() -> None:
    llm = FakeLLM(
        [
            FinalAnswer(content="Done."),
        ]
    )

    agent = AgentRunner(llm, make_executor())

    result = agent.run("Do something")

    assert result == "Done."
    assert llm.calls == 1


def test_agent_executes_tool_then_finishes() -> None:
    llm = FakeLLM(
        [
            ToolCall(
                tool_name="example",
                arguments={"value": 5},
            ),
            FinalAnswer(content="The result is 10."),
        ]
    )

    agent = AgentRunner(llm, make_executor())

    result = agent.run("Calculate something")

    assert result == "The result is 10."
    assert llm.calls == 2


def test_agent_stops_at_max_steps() -> None:
    llm = FakeLLM(
        [
            ToolCall(
                tool_name="example",
                arguments={"value": 1},
            )
        ]
        * 3
    )

    agent = AgentRunner(
        llm,
        make_executor(),
        max_steps=2,
    )

    with pytest.raises(RuntimeError, match="maximum steps"):
        agent.run("Loop forever")

from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder


def test_agent_records_execution_events() -> None:
    recorder = EventRecorder()

    runner = AgentRunner(
        llm=FakeLLM(
            responses=[
                FinalAnswer(content="done"),
            ]
        ),
        tool_executor=tool_executor,
        event_recorder=recorder,
    )

    result = runner.run("test task")

    assert result == "done"

    events = recorder.all_events()

    assert [event.event_type for event in events] == [
        EventType.RUN_STARTED,
        EventType.MODEL_CALLED,
        EventType.RUN_COMPLETED,
    ]

    assert all(event.run_id == events[0].run_id for event in events)


def test_agent_records_model_usage_and_latency() -> None:
    recorder = EventRecorder()
    usage = LLMUsage(input_tokens=120, output_tokens=42, total_tokens=162)
    runner = AgentRunner(
        llm=FakeLLM(responses=[FinalAnswer(content="done", usage=usage)]),
        tool_executor=tool_executor,
        event_recorder=recorder,
    )

    runner.run("test task")

    model_event = next(
        event
        for event in recorder.all_events()
        if event.event_type == EventType.MODEL_CALLED
    )

    assert "duration_ms" in model_event.metadata
    assert model_event.metadata["input_tokens"] == 120
    assert model_event.metadata["output_tokens"] == 42
    assert model_event.metadata["total_tokens"] == 162
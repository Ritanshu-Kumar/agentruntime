from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer, ToolCall
from app.application.retry import RetryPolicy
from app.application.tool_executor import ToolExecutor
from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder
from app.domain.tools.base import Tool, ToolResult
from app.domain.tools.errors import ToolTransientError
from app.domain.tools.registry import ToolRegistry


class FlakyToolInput:
    pass


class FlakyTool(Tool[FlakyToolInput]):
    name = "flaky"
    description = "A tool that fails twice and then succeeds."
    input_schema = FlakyToolInput
    permissions = set()

    def __init__(self):
        self.calls = 0

    def execute(self, arguments):
        self.calls += 1

        if self.calls < 3:
            raise ToolTransientError("temporary failure")

        return ToolResult.ok("recovered")


def test_agent_recovers_from_transient_tool_failure():
    registry = ToolRegistry()

    tool = FlakyTool()
    registry.register(tool)

    executor = ToolExecutor(
        registry,
        set(),
        RetryPolicy(max_attempts=3),
    )

    llm = FakeLLM(
        [
            ToolCall(
                tool_name="flaky",
                arguments={},
            ),
            FinalAnswer(
                content="Recovered successfully."
            ),
        ]
    )

    agent = AgentRunner(
        llm,
        executor,
    )

    result = agent.run("Recover from failure")

    assert result == "Recovered successfully."
    assert tool.calls == 3


def test_agent_records_retries_with_its_recorder():
    registry = ToolRegistry()
    tool = FlakyTool()
    registry.register(tool)

    recorder = EventRecorder()
    executor = ToolExecutor(
        registry=registry,
        permissions=set(),
        retry_policy=RetryPolicy(max_attempts=3),
    )
    agent = AgentRunner(
        llm=FakeLLM(
            responses=[
                ToolCall(tool_name="flaky", arguments={}),
                FinalAnswer(content="Recovered successfully."),
            ]
        ),
        tool_executor=executor,
        event_recorder=recorder,
    )

    assert agent.run("Recover from failure") == "Recovered successfully."

    run_id = recorder.all_events()[0].run_id
    retry_events = [
        event
        for event in recorder.events(run_id)
        if event.event_type == EventType.RETRY
    ]
    assert len(retry_events) == 2
    assert retry_events[0].metadata["attempt"] == 1
    assert retry_events[1].metadata["attempt"] == 2
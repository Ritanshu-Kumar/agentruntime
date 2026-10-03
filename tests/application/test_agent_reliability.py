from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer, ToolCall
from app.application.retry import RetryPolicy
from app.application.tool_executor import ToolExecutor
from app.domain.tools.base import Tool, ToolResult
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
            raise RuntimeError("temporary failure")

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
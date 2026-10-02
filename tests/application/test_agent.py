import pytest
from pydantic import BaseModel

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer, ToolCall
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
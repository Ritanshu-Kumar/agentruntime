from pydantic import BaseModel

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer, ToolCall
from app.application.tool_executor import ToolExecutor
from app.domain.tools import Permission, Tool, ToolRegistry, ToolResult


class AddInput(BaseModel):
    a: int
    b: int


class AddTool(Tool[AddInput]):
    name = "add"
    description = "Add two numbers."
    input_schema = AddInput
    permissions = frozenset()

    def execute(self, arguments: AddInput) -> ToolResult:
        return ToolResult.ok(arguments.a + arguments.b)


def test_complete_agent_pipeline() -> None:
    registry = ToolRegistry()
    registry.register(AddTool())

    executor = ToolExecutor(
        registry,
        set(),
    )

    llm = FakeLLM(
        [
            ToolCall(
                tool_name="add",
                arguments={
                    "a": 20,
                    "b": 22,
                },
            ),
            FinalAnswer(
                content="The answer is 42."
            ),
        ]
    )

    agent = AgentRunner(llm, executor)

    result = agent.run("What is 20 + 22?")

    assert result == "The answer is 42."
    assert llm.calls == 2
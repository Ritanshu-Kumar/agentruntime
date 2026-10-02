import pytest

from app.application.llm import (
    FakeLLM,
    FinalAnswer,
    ToolCall,
)


def test_tool_call() -> None:
    response = ToolCall(
        tool_name="read_file",
        arguments={"path": "README.md"},
    )

    assert response.type == "tool_call"
    assert response.tool_name == "read_file"
    assert response.arguments["path"] == "README.md"


def test_final_answer() -> None:
    response = FinalAnswer(
        content="Task complete."
    )

    assert response.type == "final_answer"
    assert response.content == "Task complete."


def test_fake_llm_returns_responses_in_order() -> None:
    llm = FakeLLM(
        [
            ToolCall(
                tool_name="read_file",
                arguments={"path": "README.md"},
            ),
            FinalAnswer(content="Done."),
        ]
    )

    first = llm.respond([])
    second = llm.respond([])

    assert first.tool_name == "read_file"
    assert second.content == "Done."
    assert llm.calls == 2


def test_fake_llm_fails_when_empty() -> None:
    llm = FakeLLM([])

    with pytest.raises(RuntimeError):
        llm.respond([])
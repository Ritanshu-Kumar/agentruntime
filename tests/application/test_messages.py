from app.application.messages import (
    AssistantMessage,
    ToolMessage,
    UserMessage,
)


def test_user_message() -> None:
    message = UserMessage(content="Hello")

    assert message.role == "user"
    assert message.content == "Hello"


def test_assistant_message() -> None:
    message = AssistantMessage(content="Hi")

    assert message.role == "assistant"
    assert message.content == "Hi"


def test_tool_message() -> None:
    message = ToolMessage(
        tool_name="read_file",
        success=True,
        content="hello",
    )

    assert message.role == "tool"
    assert message.tool_name == "read_file"
    assert message.success is True
    assert message.content == "hello"
from app.infrastructure.db.message_models import MessageRecord


def test_message_record() -> None:
    message = MessageRecord(
        run_id="123",
        role="tool",
        content="hello",
        tool_name="read_file",
        success=True,
    )

    assert message.run_id == "123"
    assert message.role == "tool"
    assert message.tool_name == "read_file"
    assert message.success is True
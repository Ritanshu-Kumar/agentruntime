import json
import logging
from datetime import datetime

from app.logging_config import JsonFormatter


def test_json_formatter_includes_standard_and_allowed_fields() -> None:
    record = logging.LogRecord(
        name="app.application.agent",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Agent run completed",
        args=(),
        exc_info=None,
    )
    record.event = "run.completed"
    record.run_id = "run-123"
    record.secret = "must-not-be-logged"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.application.agent"
    assert payload["message"] == "Agent run completed"
    assert payload["event"] == "run.completed"
    assert payload["run_id"] == "run-123"
    assert "secret" not in payload

    timestamp = datetime.fromisoformat(
        payload["timestamp"].replace("Z", "+00:00")
    )
    assert timestamp.utcoffset().total_seconds() == 0


def test_json_formatter_includes_tool_metadata() -> None:
    record = logging.LogRecord(
        name="app.application.agent",
        level=logging.INFO,
        pathname=__file__,
        lineno=20,
        msg="Tool execution completed",
        args=(),
        exc_info=None,
    )
    record.event = "tool.completed"
    record.tool_name = "example"
    record.duration_ms = 12.5
    record.success = True

    payload = json.loads(JsonFormatter().format(record))

    assert payload["event"] == "tool.completed"
    assert payload["tool_name"] == "example"
    assert payload["duration_ms"] == 12.5
    assert payload["success"] is True

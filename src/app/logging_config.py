import json
import logging
from datetime import datetime, timezone
from typing import Any


_ALLOWED_FIELDS = (
    "event",
    "run_id",
    "tool_name",
    "duration_ms",
    "success",
    "error_type",
    "input_tokens",
    "output_tokens",
    "total_tokens",
)


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for field in _ALLOWED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__

        return json.dumps(payload, separators=(",", ":"), default=str)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(JsonFormatter())

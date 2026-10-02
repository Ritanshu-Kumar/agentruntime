from datetime import datetime, timezone

from app.infrastructure.db.models import Base, RunRecord


def test_run_record_metadata() -> None:
    assert "runs" in Base.metadata.tables


def test_run_record_can_be_created() -> None:
    now = datetime.now(timezone.utc)

    record = RunRecord(
        id="123",
        task="test",
        status="pending",
        created_at=now,
        updated_at=now,
    )

    assert record.id == "123"
    assert record.task == "test"
    assert record.status == "pending"
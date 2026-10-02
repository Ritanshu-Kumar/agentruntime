from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.domain.runs import Run, RunStatus
from app.infrastructure.db.models import Base
from app.infrastructure.postgres_run_repository import (
    PostgresRunRepository,
)


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_create_and_get() -> None:
    session = create_session()
    repository = PostgresRunRepository(session)

    run = Run(task="test")

    repository.create(run)

    result = repository.get(run.id)

    assert result is not None
    assert result.id == run.id
    assert result.task == "test"
    assert result.status == RunStatus.PENDING


def test_get_missing_run() -> None:
    session = create_session()
    repository = PostgresRunRepository(session)

    result = repository.get(Run(task="test").id)

    assert result is None


def test_save() -> None:
    session = create_session()
    repository = PostgresRunRepository(session)

    run = Run(task="original")

    repository.create(run)

    run.task = "updated"
    run.status = RunStatus.COMPLETED

    repository.save(run)

    result = repository.get(run.id)

    assert result is not None
    assert result.task == "updated"
    assert result.status == RunStatus.COMPLETED


def test_save_missing_run_fails() -> None:
    session = create_session()
    repository = PostgresRunRepository(session)

    run = Run(task="missing")

    try:
        repository.save(run)
        assert False
    except ValueError:
        pass
from uuid import uuid4

import pytest

from app.domain.runs import Run
from app.infrastructure.runs_repository import InMemoryRunRepository


def test_create_and_get() -> None:
    repository = InMemoryRunRepository()
    run = Run(task="test")

    repository.create(run)

    assert repository.get(run.id) == run


def test_get_missing_run() -> None:
    repository = InMemoryRunRepository()

    assert repository.get(uuid4()) is None


def test_duplicate_create_fails() -> None:
    repository = InMemoryRunRepository()
    run = Run(task="test")

    repository.create(run)

    with pytest.raises(ValueError):
        repository.create(run)


def test_save_updates_run() -> None:
    repository = InMemoryRunRepository()
    run = Run(task="test")

    repository.create(run)

    run.task = "updated"
    repository.save(run)

    result = repository.get(run.id)

    assert result is not None
    assert result.task == "updated"


def test_save_missing_run_fails() -> None:
    repository = InMemoryRunRepository()

    with pytest.raises(ValueError):
        repository.save(Run(task="missing"))
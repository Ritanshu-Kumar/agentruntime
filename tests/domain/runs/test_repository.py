from uuid import uuid4

import pytest

from app.domain.runs import Run
from app.domain.runs.repository import RunRepository


def test_repository_is_abstract() -> None:
    with pytest.raises(TypeError):
        RunRepository()


def test_run_repository_contract_has_expected_methods() -> None:
    assert hasattr(RunRepository, "create")
    assert hasattr(RunRepository, "get")
    assert hasattr(RunRepository, "save")
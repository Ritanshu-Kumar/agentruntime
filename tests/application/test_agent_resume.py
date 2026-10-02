from app.application.llm import FakeLLM, FinalAnswer
from app.application.messages import AssistantMessage, UserMessage
from app.domain.runs.models import Run, RunStatus
from app.domain.runs.repository import RunRepository
from app.infrastructure.runs_repository import InMemoryRunRepository


def test_saved_run_can_be_loaded_for_resume():
    repository = InMemoryRunRepository()

    run = Run(
        task="Continue my task",
        status=RunStatus.RUNNING,
        messages=[
            UserMessage(content="Continue my task"),
            AssistantMessage(content="I started working on it."),
        ],
    )

    repository.create(run)

    loaded = repository.get(run.id)

    assert loaded is not None
    assert loaded.id == run.id
    assert loaded.task == "Continue my task"
    assert loaded.status == RunStatus.RUNNING
    assert len(loaded.messages) == 2
    assert loaded.messages[0].content == "Continue my task"
    assert loaded.messages[1].content == "I started working on it."
from app.application.messages import ToolMessage, UserMessage
from app.domain.runs import Run, RunStatus
from app.infrastructure.runs_repository import InMemoryRunRepository


def test_failed_tool_message_is_persisted():
    repository = InMemoryRunRepository()
    run = Run(
        task="test failure",
        status=RunStatus.RUNNING,
        messages=[
            UserMessage(content="test failure"),
            ToolMessage(
                tool_name="python",
                success=False,
                content="execution timed out",
            ),
        ],
    )

    repository.create(run)

    loaded = repository.get(run.id)

    assert loaded is not None
    assert loaded.messages[1].success is False
    assert loaded.messages[1].content == "execution timed out"
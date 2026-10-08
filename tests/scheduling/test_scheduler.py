from datetime import datetime, timedelta, timezone

from app.application.agent import AgentRunner
from app.application.llm import FakeLLM, FinalAnswer
from app.application.scheduler import Scheduler
from app.application.tool_executor import ToolExecutor
from app.domain.scheduling.in_memory import InMemoryScheduleRepository
from app.domain.scheduling.models import ScheduledRun
from app.domain.tools.registry import ToolRegistry


def make_agent(responses: list[FinalAnswer]) -> AgentRunner:
    return AgentRunner(
        llm=FakeLLM(responses),
        tool_executor=ToolExecutor(ToolRegistry(), set()),
    )


def test_scheduler_runs_due_tasks_and_marks_them_completed() -> None:
    now = datetime.now(timezone.utc)
    repository = InMemoryScheduleRepository()
    due_run = ScheduledRun(
        task="due task",
        run_at=now - timedelta(seconds=1),
    )
    future_run = ScheduledRun(
        task="future task",
        run_at=now + timedelta(hours=1),
    )
    repository.create(due_run)
    repository.create(future_run)
    agent = make_agent([FinalAnswer(content="done")])
    scheduler = Scheduler(repository, agent)

    results = scheduler.run_due(now)

    assert results == ["done"]
    assert repository._runs[due_run.id].completed is True
    assert repository._runs[future_run.id].completed is False
    assert repository.due(now) == []


def test_scheduler_does_not_mark_failed_task_completed() -> None:
    now = datetime.now(timezone.utc)
    repository = InMemoryScheduleRepository()
    scheduled_run = repository.create(
        ScheduledRun(task="failing task", run_at=now)
    )

    scheduler = Scheduler(
        repository,
        make_agent([]),
    )

    try:
        scheduler.run_due(now)
        assert False, "Expected the agent failure to propagate"
    except RuntimeError as exc:
        assert str(exc) == "FakeLLM has no responses remaining."

    stored = repository._runs[scheduled_run.id]
    assert stored.completed is False

from collections import Counter

from fastapi import APIRouter, Depends

from app.api.auth import require_api_key
from app.api.dependencies import get_agent_runner
from app.application.agent import AgentRunner


router = APIRouter(
    tags=["monitoring"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/metrics")
def runtime_metrics(
    runner: AgentRunner = Depends(get_agent_runner),
) -> dict:
    repository = runner.run_repository
    recorder = runner.event_recorder

    event_counts: Counter[str] = Counter()
    run_event_counts: Counter[str] = Counter()

    if recorder is not None:
        events = recorder.all_events()
    else:
        events = []

    for event in events:
        event_counts[event.event_type.value] += 1

        if event.event_type.value in {
            "run.started",
            "run.completed",
            "run.failed",
        }:
            run_event_counts[event.event_type.value] += 1

    return {
        "status": "ok",
        "observation_source": (
            "event_recorder"
            if recorder is not None
            else "none"
        ),
        "runs": {
            "started": run_event_counts["run.started"],
            "completed": run_event_counts["run.completed"],
            "failed": run_event_counts["run.failed"],
        },
        "events": dict(event_counts),
        "repository_configured": repository is not None,
    }
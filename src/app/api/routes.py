from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import require_api_key
from app.api.dependencies import get_agent_runner
from app.api.schemas import (
    CreateRunRequest,
    ResumeRunRequest,
    RunResponse,
)
from app.application.agent import AgentRunner
from app.domain.approval.errors import ApprovalRequiredError
from app.domain.runs.models import RunStatus


router = APIRouter(
    prefix="/runs",
    tags=["runs"],
    dependencies=[Depends(require_api_key)],
)


def _answer_from_run(run) -> str | None:
    for message in reversed(run.messages):
        if getattr(message, "role", None) == "assistant":
            content = getattr(message, "content", None)

            if content and not content.startswith(
                "Calling tool:"
            ):
                return content

    return None


def _to_response(run) -> RunResponse:
    return RunResponse(
        id=run.id,
        task=run.task,
        status=run.status,
        created_at=run.created_at,
        updated_at=run.updated_at,
        answer=_answer_from_run(run),
    )


@router.post(
    "",
    response_model=RunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_run(
    request: CreateRunRequest,
    runner: AgentRunner = Depends(get_agent_runner),
):
    try:
        runner.run(request.task)

    except ApprovalRequiredError:
        pass

    except Exception as exc:
        if runner.run_repository is None:
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc

    if runner.last_run_id is None:
        raise HTTPException(
            status_code=500,
            detail="Agent did not create a run",
        )

    if runner.run_repository is None:
        raise HTTPException(
            status_code=500,
            detail="Run repository is not configured",
        )

    run = runner.run_repository.get(
        runner.last_run_id
    )

    if run is None:
        raise HTTPException(
            status_code=500,
            detail="Created run could not be retrieved",
        )

    return _to_response(run)


@router.get(
    "/{run_id}",
    response_model=RunResponse,
)
def get_run(
    run_id: UUID,
    runner: AgentRunner = Depends(get_agent_runner),
):
    if runner.run_repository is None:
        raise HTTPException(
            status_code=500,
            detail="Run repository is not configured",
        )

    run = runner.run_repository.get(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found",
        )

    return _to_response(run)


@router.post(
    "/{run_id}/resume",
    response_model=RunResponse,
)
def resume_run(
    run_id: UUID,
    request: ResumeRunRequest,
    runner: AgentRunner = Depends(get_agent_runner),
):
    if runner.run_repository is None:
        raise HTTPException(
            status_code=500,
            detail="Run repository is not configured",
        )

    run = runner.run_repository.get(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found",
        )

    try:
        runner.resume(request.approval_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    updated = runner.run_repository.get(run_id)

    if updated is None:
        raise HTTPException(
            status_code=500,
            detail="Run disappeared after resume",
        )

    return _to_response(updated)
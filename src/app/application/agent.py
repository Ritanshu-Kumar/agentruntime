from time import perf_counter

from app.application.llm import FinalAnswer, LLMClient, ToolCall
from app.application.messages import AssistantMessage, UserMessage
from app.application.tool_executor import ToolExecutor
from app.domain.observability.events import EventType
from app.domain.observability.recorder import EventRecorder
from app.domain.runs.models import Run
from app.domain.runs.repository import RunRepository


class AgentRunner:
    def __init__(
        self,
        llm: LLMClient,
        tool_executor: ToolExecutor,
        run_repository: RunRepository | None = None,
        event_recorder: EventRecorder | None = None,
        max_steps: int = 10,
    ):
        self.llm = llm
        self.tool_executor = tool_executor
        self.run_repository = run_repository
        self.event_recorder = event_recorder
        self.max_steps = max_steps

    def run(self, task: str) -> str:
        run = Run(task=task)

        if self.event_recorder:
            self.event_recorder.record(
                run.id,
                EventType.RUN_STARTED,
            )

        if self.run_repository:
            run.status = "running"
            run.touch()
            self.run_repository.create(run)

        run.messages.append(UserMessage(content=task))

        if self.run_repository:
            run.touch()
            self.run_repository.save(run)

        for _ in range(self.max_steps):
            started = perf_counter()
            try:
                response = self.llm.respond(
                    [message.model_dump() for message in run.messages]
                )
            except Exception as exc:
                if self.event_recorder:
                    self.event_recorder.record(
                        run.id,
                        EventType.RUN_FAILED,
                        {
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        },
                    )
                raise

            duration_ms = (perf_counter() - started) * 1000
            usage = getattr(response, "usage", None)

            if self.event_recorder:
                self.event_recorder.record(
                    run.id,
                    EventType.MODEL_CALLED,
                    {
                        "duration_ms": duration_ms,
                        "input_tokens": usage.input_tokens if usage else 0,
                        "output_tokens": usage.output_tokens if usage else 0,
                        "total_tokens": usage.total_tokens if usage else 0,
                    },
                )

            if isinstance(response, FinalAnswer):
                run.messages.append(
                    AssistantMessage(content=response.content)
                )
                run.status = "completed"
                run.touch()

                if self.event_recorder:
                    self.event_recorder.record(
                        run.id,
                        EventType.RUN_COMPLETED,
                    )

                if self.run_repository:
                    self.run_repository.save(run)

                return response.content

            if isinstance(response, ToolCall):
                run.messages.append(
                    AssistantMessage(
                        content=f"Calling tool: {response.tool_name}"
                    )
                )

                tool_started = perf_counter()
                tool_message = self.tool_executor.execute(
                    response,
                    run_id=run.id,
                )
                tool_duration_ms = (perf_counter() - tool_started) * 1000

                if self.event_recorder:
                    self.event_recorder.record(
                        run.id,
                        EventType.TOOL_CALLED,
                        {
                            "tool_name": response.tool_name,
                            "duration_ms": tool_duration_ms,
                        },
                    )
                    self.event_recorder.record(
                        run.id,
                        EventType.TOOL_COMPLETED,
                        {
                            "tool_name": response.tool_name,
                            "duration_ms": tool_duration_ms,
                            "success": tool_message.success,
                        },
                    )

                run.messages.append(tool_message)
                run.touch()

                if self.run_repository:
                    self.run_repository.save(run)

        run.status = "failed"
        run.touch()

        if self.event_recorder:
            self.event_recorder.record(
                run.id,
                EventType.RUN_FAILED,
                {"reason": "maximum steps exceeded"},
            )

        if self.run_repository:
            self.run_repository.save(run)

        raise RuntimeError("maximum steps exceeded")
from app.application.llm import FinalAnswer, LLMClient, ToolCall
from app.application.messages import AssistantMessage, UserMessage
from app.application.tool_executor import ToolExecutor
from app.domain.runs.models import Run
from app.domain.runs.repository import RunRepository


class AgentRunner:
    def __init__(
        self,
        llm: LLMClient,
        tool_executor: ToolExecutor,
        run_repository: RunRepository | None = None,
        max_steps: int = 10,
    ):
        self.llm = llm
        self.tool_executor = tool_executor
        self.run_repository = run_repository
        self.max_steps = max_steps

    def run(self, task: str) -> str:
        run = Run(task=task)

        if self.run_repository:
            run.status = "running"
            run.touch()
            self.run_repository.create(run)

        run.messages.append(UserMessage(content=task))

        if self.run_repository:
            run.touch()
            self.run_repository.save(run)

        for _ in range(self.max_steps):
            response = self.llm.respond(
                [message.model_dump() for message in run.messages]
            )

            if isinstance(response, FinalAnswer):
                run.messages.append(
                    AssistantMessage(content=response.content)
                )
                run.status = "completed"
                run.touch()

                if self.run_repository:
                    self.run_repository.save(run)

                return response.content

            if isinstance(response, ToolCall):
                run.messages.append(
                    AssistantMessage(
                        content=f"Calling tool: {response.tool_name}"
                    )
                )

                tool_message = self.tool_executor.execute(response)
                run.messages.append(tool_message)

                run.touch()

                if self.run_repository:
                    self.run_repository.save(run)

        run.status = "failed"
        run.touch()

        if self.run_repository:
            self.run_repository.save(run)

        raise RuntimeError("maximum steps exceeded")
from app.application.llm import FinalAnswer, LLMClient, ToolCall
from app.application.messages import (
    AssistantMessage,
    Message,
    ToolMessage,
    UserMessage,
)
from app.application.tool_executor import ToolExecutor


class AgentRunner:
    def __init__(
        self,
        llm: LLMClient,
        tool_executor: ToolExecutor,
        max_steps: int = 10,
    ) -> None:
        self.llm = llm
        self.tool_executor = tool_executor
        self.max_steps = max_steps

    def run(self, task: str) -> str:
        messages: list[Message] = [
            UserMessage(content=task),
        ]

        for _ in range(self.max_steps):
            response = self.llm.respond(
                [message.model_dump() for message in messages]
            )

            if isinstance(response, FinalAnswer):
                messages.append(
                    AssistantMessage(content=response.content)
                )
                return response.content

            if isinstance(response, ToolCall):
                messages.append(
                    AssistantMessage(
                        content=f"Calling tool: {response.tool_name}"
                    )
                )

                result = self.tool_executor.execute(response)
                messages.append(result)
                continue

        raise RuntimeError("Agent exceeded maximum steps.")
from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel


class LLMUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ToolCall(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    tool_name: str
    arguments: dict[str, Any]
    usage: LLMUsage | None = None


class FinalAnswer(BaseModel):
    type: Literal["final_answer"] = "final_answer"
    content: str
    usage: LLMUsage | None = None


LLMResponse = ToolCall | FinalAnswer


class LLMClient(ABC):
    @abstractmethod
    def respond(self, messages: list[dict[str, str]]) -> LLMResponse:
        raise NotImplementedError


class FakeLLM(LLMClient):
    def __init__(self, responses: list[LLMResponse]) -> None:
        self.responses = list(responses)
        self.calls = 0

    def respond(self, messages: list[dict[str, str]]) -> LLMResponse:
        if not self.responses:
            raise RuntimeError("FakeLLM has no responses remaining.")

        self.calls += 1
        return self.responses.pop(0)
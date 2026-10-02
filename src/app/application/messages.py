from typing import Literal

from pydantic import BaseModel


class UserMessage(BaseModel):
    role: Literal["user"] = "user"
    content: str


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str


class ToolMessage(BaseModel):
    role: Literal["tool"] = "tool"
    tool_name: str
    success: bool
    content: str


Message = UserMessage | AssistantMessage | ToolMessage
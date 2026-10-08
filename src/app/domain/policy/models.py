from pydantic import BaseModel, Field


class AgentPolicy(BaseModel):
    max_steps: int = Field(default=10, ge=1)
    max_tool_calls: int = Field(default=20, ge=1)
    allow_parallel_tools: bool = False
    allow_memory: bool = True
    require_approval_for_sensitive: bool = True
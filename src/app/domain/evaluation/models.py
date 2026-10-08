from uuid import UUID

from pydantic import BaseModel, Field


class BenchmarkTask(BaseModel):
    name: str
    task: str
    expected_answer: str
    expected_tools: list[str] = Field(default_factory=list)
    expected_tool_arguments: list[dict] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    benchmark_name: str
    run_id: UUID
    actual_answer: str
    answer_correct: bool

    expected_tools: list[str]
    actual_tools: list[str]
    tools_correct: bool

    expected_tool_arguments: list[dict]
    actual_tool_arguments: list[dict]
    arguments_correct: bool

    success: bool
from app.domain.memory.models import Memory


def format_memory_context(memories: list[Memory]) -> str:
    if not memories:
        return ""

    lines = ["Relevant memory:"]
    for memory in memories:
        lines.append(f"- {memory.key}: {memory.value}")
    return "\n".join(lines)

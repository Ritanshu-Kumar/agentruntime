from enum import StrEnum


class SafetyLevel(StrEnum):
    SAFE = "safe"
    SENSITIVE = "sensitive"
    DANGEROUS = "dangerous"


class SafetyPolicy:
    """Decides whether a tool may execute automatically."""

    def __init__(
        self,
        *,
        blocked_levels: set[SafetyLevel] | None = None,
    ) -> None:
        self.blocked_levels = blocked_levels or {
            SafetyLevel.SENSITIVE,
            SafetyLevel.DANGEROUS,
        }

    def allows(self, level: SafetyLevel) -> bool:
        return level not in self.blocked_levels
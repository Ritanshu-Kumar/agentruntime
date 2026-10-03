from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

    def should_retry(self, attempt: int, retryable: bool) -> bool:
        return retryable and attempt < self.max_attempts
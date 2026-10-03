from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    def should_retry(self, attempt: int, retryable: bool) -> bool:
        return retryable and attempt < self.max_attempts
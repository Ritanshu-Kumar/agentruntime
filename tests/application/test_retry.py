from app.application.retry import RetryPolicy


def test_retry_policy_retries_before_max_attempts():
    policy = RetryPolicy(max_attempts=3)

    assert policy.should_retry(1, True) is True
    assert policy.should_retry(2, True) is True
    assert policy.should_retry(3, True) is False


def test_retry_policy_does_not_retry_non_retryable_failure():
    policy = RetryPolicy(max_attempts=3)

    assert policy.should_retry(1, False) is False
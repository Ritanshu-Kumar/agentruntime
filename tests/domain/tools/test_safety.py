from app.domain.tools.safety import SafetyLevel, SafetyPolicy


def test_default_policy_allows_safe_actions():
    policy = SafetyPolicy()

    assert policy.allows(SafetyLevel.SAFE)


def test_default_policy_blocks_sensitive_actions():
    policy = SafetyPolicy()

    assert not policy.allows(SafetyLevel.SENSITIVE)


def test_default_policy_blocks_dangerous_actions():
    policy = SafetyPolicy()

    assert not policy.allows(SafetyLevel.DANGEROUS)


def test_policy_can_allow_sensitive_actions():
    policy = SafetyPolicy(
        blocked_levels={SafetyLevel.DANGEROUS}
    )

    assert policy.allows(SafetyLevel.SAFE)
    assert policy.allows(SafetyLevel.SENSITIVE)
    assert not policy.allows(SafetyLevel.DANGEROUS)
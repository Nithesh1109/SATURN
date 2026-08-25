from saturn.runtime.safe_mode import SafeModePolicy


def test_safe_mode_allows_low_risk_desktop_actions() -> None:
    policy = SafeModePolicy()
    assert policy.check("mouse_move", 0) == (True, None)
    assert policy.check("take_screenshot", 1) == (True, None)


def test_safe_mode_blocks_unapproved_tools() -> None:
    policy = SafeModePolicy()
    allowed, reason = policy.check("shutdown_computer", 0)
    assert allowed is False
    assert "not permitted" in reason


def test_safe_mode_limits_actions() -> None:
    policy = SafeModePolicy(max_actions=2)
    allowed, reason = policy.check("mouse_click", 2)
    assert allowed is False
    assert "limit" in reason


def test_safe_mode_can_be_disabled_for_future_controlled_use() -> None:
    policy = SafeModePolicy(enabled=False)
    assert policy.check("shutdown_computer", 100) == (True, None)

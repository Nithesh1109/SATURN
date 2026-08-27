from saturn.security.permissions import RiskLevel
from saturn.security.policy import PermissionEngine


def test_low_risk_action_is_allowed_without_confirmation() -> None:
    decision = PermissionEngine().decide("mouse_move", {"x": 10, "y": 10})
    assert decision.allowed is True
    assert decision.risk is RiskLevel.LOW


def test_high_risk_action_requires_explicit_confirmation() -> None:
    decision = PermissionEngine().decide("delete_file", {"path": "x.txt"})
    assert decision.allowed is False
    assert decision.requires_confirmation is True
    assert decision.risk is RiskLevel.HIGH


def test_critical_action_requires_confirmation() -> None:
    decision = PermissionEngine().decide("shutdown_computer", {})
    assert decision.allowed is False
    assert decision.risk is RiskLevel.CRITICAL


def test_unknown_tools_fail_closed() -> None:
    decision = PermissionEngine().decide("unknown_tool", {})
    assert decision.allowed is False
    assert decision.requires_confirmation is False
    assert decision.risk is RiskLevel.HIGH
    assert decision.reason is not None


def test_custom_tool_must_explicitly_declare_risk() -> None:
    decision = PermissionEngine().decide(
        "custom_safe_tool", {}, declared_risk=RiskLevel.LOW
    )
    assert decision.allowed is True
    assert decision.risk is RiskLevel.LOW


def test_custom_high_risk_tool_requires_confirmation() -> None:
    decision = PermissionEngine().decide(
        "custom_destructive_tool", {}, declared_risk=RiskLevel.HIGH
    )
    assert decision.allowed is False
    assert decision.requires_confirmation is True
    assert decision.risk is RiskLevel.HIGH

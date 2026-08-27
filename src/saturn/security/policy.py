"""Central permission policy for SATURN tool execution."""

from __future__ import annotations

from dataclasses import dataclass

from .permissions import RiskLevel


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    requires_confirmation: bool = False
    reason: str | None = None
    risk: RiskLevel = RiskLevel.LOW


class PermissionEngine:
    """Classify tools and enforce confirmation/deny policy at one boundary."""

    _RISK: dict[str, RiskLevel] = {
        "open_application": RiskLevel.MEDIUM,
        "close_application": RiskLevel.HIGH,
        "create_folder": RiskLevel.LOW,
        "create_file": RiskLevel.LOW,
        "copy_file": RiskLevel.LOW,
        "move_file": RiskLevel.MEDIUM,
        "delete_file": RiskLevel.HIGH,
        "mouse_move": RiskLevel.LOW,
        "mouse_click": RiskLevel.LOW,
        "mouse_scroll": RiskLevel.LOW,
        "keyboard_type": RiskLevel.MEDIUM,
        "keyboard_press": RiskLevel.MEDIUM,
        "clipboard_read": RiskLevel.LOW,
        "clipboard_write": RiskLevel.MEDIUM,
        "take_screenshot": RiskLevel.LOW,
        "lock_computer": RiskLevel.CRITICAL,
        "shutdown_computer": RiskLevel.CRITICAL,
    }

    _CONFIRMATION_REQUIRED = {RiskLevel.HIGH, RiskLevel.CRITICAL}

    def decide(self, tool_name: str, arguments: dict[str, object]) -> PermissionDecision:
        risk = self._RISK.get(tool_name, RiskLevel.HIGH)
        if risk in self._CONFIRMATION_REQUIRED and arguments.get("confirmation") is not True:
            return PermissionDecision(
                allowed=False,
                requires_confirmation=True,
                reason=f"{tool_name} requires explicit confirmation",
                risk=risk,
            )
        return PermissionDecision(allowed=True, risk=risk)

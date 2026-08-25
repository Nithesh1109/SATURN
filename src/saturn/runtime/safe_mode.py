"""Controlled execution policy for SATURN's first real desktop tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SafeModePolicy:
    """Allow only explicitly approved low-risk actions during real testing."""

    enabled: bool = True
    allowed_tools: frozenset[str] = frozenset({"mouse_move", "mouse_click", "take_screenshot"})
    max_actions: int = 3

    def check(self, tool_name: str, action_count: int) -> tuple[bool, str | None]:
        if not self.enabled:
            return True, None
        if action_count >= self.max_actions:
            return False, "Safe mode action limit reached"
        if tool_name not in self.allowed_tools:
            return False, f"Tool not permitted in safe mode: {tool_name}"
        return True, None

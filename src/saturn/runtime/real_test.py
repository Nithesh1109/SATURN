"""Small, explicit entry points for SATURN's first real desktop smoke test."""

from __future__ import annotations

from dataclasses import dataclass

from saturn.tools.base import ToolContext
from saturn.runtime.safe_mode import SafeModePolicy


@dataclass(frozen=True)
class RealTestResult:
    success: bool
    message: str


class RealDesktopSmokeTest:
    """Run only the harmless real-screen steps approved for 4D."""

    def __init__(self, *, screenshot_tool, safe_mode: SafeModePolicy | None = None) -> None:
        self._screenshot = screenshot_tool
        self._safe_mode = safe_mode or SafeModePolicy()
        self._actions = 0

    def capture_screen(self, path: str = "saturn_real_test.png") -> RealTestResult:
        allowed, reason = self._safe_mode.check("take_screenshot", self._actions)
        if not allowed:
            return RealTestResult(False, reason or "Safe mode rejected screenshot")

        result = self._screenshot.execute({"path": path}, ToolContext())
        if not result.success:
            return RealTestResult(False, result.error or "Screenshot failed")

        self._actions += 1
        return RealTestResult(True, f"Real screenshot captured: {result.output}")

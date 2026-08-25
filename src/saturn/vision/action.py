"""Vision-guided desktop action orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from saturn.tools.base import ToolContext, ToolResult

from .perception import ScreenCapture, VisionProvider
from .targets import TargetValidator, VisualTarget
from .verification import VerificationResult, VisualVerifier


@dataclass(frozen=True)
class VisionActionResult:
    executed: bool
    target: VisualTarget | None = None
    verification: VerificationResult | None = None
    error: str | None = None


class VisionActionController:
    """Find a target visually, execute a mouse action, and verify the result."""

    def __init__(
        self,
        *,
        vision_provider: VisionProvider,
        mouse_click_tool,
        screenshot_capture,
        target_validator: TargetValidator | None = None,
        verifier: VisualVerifier | None = None,
    ) -> None:
        self._vision = vision_provider
        self._mouse_click = mouse_click_tool
        self._capture = screenshot_capture
        self._targets = target_validator or TargetValidator()
        self._verifier = verifier or VisualVerifier(vision_provider)

    def click_target(
        self,
        *,
        label: str,
        capture: ScreenCapture,
        context: ToolContext,
        verify: bool = True,
    ) -> VisionActionResult:
        observation = self._vision.analyze(capture)
        matches: list[VisualTarget] = []
        for raw_target in observation.targets:
            try:
                target = self._targets.validate(
                    raw_target, width=capture.width, height=capture.height
                )
            except ValueError:
                continue
            if target.label.casefold() == label.strip().casefold():
                matches.append(target)

        if not matches:
            return VisionActionResult(False, error=f"Could not find a safe visual target: {label}")

        target = max(matches, key=lambda item: item.confidence)
        result: ToolResult = self._mouse_click.execute(
            {"x": target.x, "y": target.y}, context
        )
        if not result.success:
            return VisionActionResult(False, target=target, error=result.error)

        verification = None
        if verify:
            try:
                fresh_capture = self._capture.capture()
                verification = self._verifier.verify_target_visible(
                    fresh_capture, label=label
                )
            except Exception as exc:
                return VisionActionResult(
                    True, target=target, error=f"Action executed but verification failed: {exc}"
                )

        return VisionActionResult(True, target=target, verification=verification)

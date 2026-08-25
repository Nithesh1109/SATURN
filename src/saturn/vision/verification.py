"""Visual verification for SATURN desktop actions."""

from __future__ import annotations

from dataclasses import dataclass

from .perception import ScreenCapture, ScreenObservation, VisionProvider


@dataclass(frozen=True)
class VerificationResult:
    verified: bool
    reason: str


class VisualVerifier:
    """Compare an expected visual condition with a fresh screen observation."""

    def __init__(self, vision_provider: VisionProvider) -> None:
        self._vision_provider = vision_provider

    def verify_target_visible(
        self,
        capture: ScreenCapture,
        *,
        label: str,
        minimum_confidence: float = 0.7,
    ) -> VerificationResult:
        observation: ScreenObservation = self._vision_provider.analyze(capture)
        wanted = label.strip().lower()
        for target in observation.targets:
            target_label = str(target.get("label", "")).strip().lower()
            try:
                confidence = float(target.get("confidence", 0.0))
            except (TypeError, ValueError):
                confidence = 0.0
            if target_label == wanted and confidence >= minimum_confidence:
                return VerificationResult(True, f"{label} visible with confidence {confidence:.2f}")

        return VerificationResult(False, f"{label} was not confidently detected")

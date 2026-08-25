"""Validation and normalization of visual targets returned by SATURN vision."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VisualTarget:
    label: str
    x: int
    y: int
    confidence: float


class TargetValidator:
    """Turn untrusted vision output into safe screen coordinates."""

    def validate(self, target: dict[str, Any], *, width: int, height: int) -> VisualTarget:
        if not isinstance(target, dict):
            raise ValueError("visual target must be an object")

        label = str(target.get("label", "")).strip()
        if not label:
            raise ValueError("visual target label is required")

        try:
            x = int(target["x"])
            y = int(target["y"])
            confidence = float(target.get("confidence", 0.0))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("visual target coordinates and confidence must be numeric") from exc

        if width <= 0 or height <= 0:
            raise ValueError("screen dimensions must be positive")
        if not 0 <= x < width or not 0 <= y < height:
            raise ValueError("visual target is outside the screen bounds")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        return VisualTarget(label=label, x=x, y=y, confidence=confidence)

    def validate_many(
        self, targets: tuple[dict[str, Any], ...], *, width: int, height: int
    ) -> tuple[VisualTarget, ...]:
        return tuple(self.validate(target, width=width, height=height) for target in targets)

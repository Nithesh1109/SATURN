"""Perception abstractions for SATURN screen understanding."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ScreenCapture:
    path: str
    width: int
    height: int

    def as_data_url(self) -> str:
        """Encode the capture as an image data URL for a vision-capable provider."""
        mime = "image/png" if self.path.lower().endswith(".png") else "image/jpeg"
        encoded = base64.b64encode(Path(self.path).read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"


@dataclass(frozen=True)
class ScreenObservation:
    """Normalized observation returned by a perception provider."""

    summary: str
    targets: tuple[dict[str, object], ...] = ()


class VisionProvider(Protocol):
    def analyze(self, capture: ScreenCapture) -> ScreenObservation:
        ...


class ScreenshotPerception:
    """Capture the screen and expose a provider-independent observation API."""

    def __init__(self, screenshot_tool) -> None:
        self._screenshot_tool = screenshot_tool

    def capture(self, path: str = "saturn_screen.png") -> ScreenCapture:
        from saturn.tools.base import ToolContext

        result = self._screenshot_tool.execute({"path": path}, ToolContext())
        if not result.success:
            raise RuntimeError(result.error or "Screenshot failed")

        image_path = Path(str(result.output))
        try:
            from PIL import Image
            with Image.open(image_path) as image:
                width, height = image.size
        except Exception as exc:
            raise RuntimeError(f"Could not inspect screenshot: {exc}") from exc

        return ScreenCapture(path=str(image_path), width=width, height=height)


class NullVisionProvider:
    """Safe placeholder until a real cloud vision model is configured."""

    def analyze(self, capture: ScreenCapture) -> ScreenObservation:
        return ScreenObservation(
            summary=f"Screen captured at {capture.width}x{capture.height}; no vision model configured.",
        )

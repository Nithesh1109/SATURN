from pathlib import Path

from PIL import Image

from saturn.tools.base import ToolContext, ToolResult
from saturn.vision.perception import NullVisionProvider, ScreenshotPerception


class FakeScreenshotTool:
    def __init__(self, path: Path) -> None:
        self.path = path

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        Image.new("RGB", (800, 600), "white").save(self.path)
        return ToolResult(success=True, output=str(self.path))


def test_screenshot_perception_returns_screen_dimensions(tmp_path) -> None:
    path = tmp_path / "screen.png"
    capture = ScreenshotPerception(FakeScreenshotTool(path)).capture(str(path))
    assert capture.path == str(path)
    assert capture.width == 800
    assert capture.height == 600


def test_null_vision_provider_is_safe_without_cloud_model(tmp_path) -> None:
    capture = type("Capture", (), {"width": 1920, "height": 1080})()
    observation = NullVisionProvider().analyze(capture)
    assert observation.targets == ()
    assert "no vision model configured" in observation.summary

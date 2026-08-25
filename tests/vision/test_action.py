from saturn.tools.base import ToolContext, ToolResult
from saturn.vision.action import VisionActionController
from saturn.vision.perception import ScreenCapture, ScreenObservation


class FakeVision:
    def __init__(self, observations):
        self.observations = iter(observations)

    def analyze(self, capture):
        return next(self.observations)


class FakeMouse:
    def __init__(self):
        self.calls = []

    def execute(self, arguments, context):
        self.calls.append(arguments)
        return ToolResult(success=True, output="clicked")


class FakeCapture:
    def __init__(self):
        self.calls = 0

    def capture(self):
        self.calls += 1
        return ScreenCapture("fresh.png", 800, 600)


def test_vision_action_clicks_highest_confidence_matching_target() -> None:
    mouse = FakeMouse()
    capture = FakeCapture()
    vision = FakeVision(
        [
            ScreenObservation(
                "desktop",
                (
                    {"label": "Chrome", "x": 100, "y": 200, "confidence": 0.7},
                    {"label": "Chrome", "x": 300, "y": 400, "confidence": 0.95},
                ),
            ),
            ScreenObservation("after click", ()),
        ]
    )
    controller = VisionActionController(
        vision_provider=vision,
        mouse_click_tool=mouse,
        screenshot_capture=capture,
    )
    result = controller.click_target(
        label="Chrome",
        capture=ScreenCapture("screen.png", 800, 600),
        context=ToolContext(),
        verify=False,
    )
    assert result.executed is True
    assert result.target.x == 300
    assert result.target.y == 400
    assert mouse.calls == [{"x": 300, "y": 400}]


def test_vision_action_rejects_target_outside_screen() -> None:
    mouse = FakeMouse()
    controller = VisionActionController(
        vision_provider=FakeVision(
            [ScreenObservation("desktop", ({"label": "Chrome", "x": 900, "y": 700, "confidence": 0.99},))]
        ),
        mouse_click_tool=mouse,
        screenshot_capture=FakeCapture(),
    )
    result = controller.click_target(
        label="Chrome",
        capture=ScreenCapture("screen.png", 800, 600),
        context=ToolContext(),
        verify=False,
    )
    assert result.executed is False
    assert mouse.calls == []


def test_vision_action_verifies_after_click() -> None:
    mouse = FakeMouse()
    capture = FakeCapture()
    vision = FakeVision(
        [
            ScreenObservation("desktop", ({"label": "Chrome", "x": 100, "y": 200, "confidence": 0.95},)),
            ScreenObservation("desktop", ({"label": "Chrome", "x": 100, "y": 200, "confidence": 0.9},)),
        ]
    )
    controller = VisionActionController(
        vision_provider=vision,
        mouse_click_tool=mouse,
        screenshot_capture=capture,
    )
    result = controller.click_target(
        label="Chrome",
        capture=ScreenCapture("screen.png", 800, 600),
        context=ToolContext(),
    )
    assert result.executed is True
    assert result.verification is not None
    assert result.verification.verified is True
    assert capture.calls == 1

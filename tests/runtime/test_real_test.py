from saturn.runtime.real_test import RealDesktopSmokeTest
from saturn.runtime.safe_mode import SafeModePolicy
from saturn.tools.base import ToolResult


class FakeScreenshot:
    def execute(self, arguments, context):
        return ToolResult(success=True, output=arguments["path"])


def test_real_desktop_smoke_test_captures_one_screen() -> None:
    test = RealDesktopSmokeTest(screenshot_tool=FakeScreenshot())
    result = test.capture_screen("screen.png")
    assert result.success is True
    assert "screen.png" in result.message


def test_real_desktop_smoke_test_respects_safe_mode() -> None:
    test = RealDesktopSmokeTest(
        screenshot_tool=FakeScreenshot(),
        safe_mode=SafeModePolicy(max_actions=0),
    )
    result = test.capture_screen()
    assert result.success is False
    assert "limit" in result.message

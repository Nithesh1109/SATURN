from saturn.tools.desktop import DesktopToolSet, KeyboardPressTool, KeyboardTypeTool, MouseClickTool, MouseMoveTool, MouseScrollTool, ScreenshotTool


def test_desktop_tool_set_has_expected_tools() -> None:
    names = {tool.name for tool in DesktopToolSet.create()}
    assert names == {
        "mouse_move",
        "mouse_click",
        "mouse_scroll",
        "keyboard_type",
        "keyboard_press",
        "take_screenshot",
    }


def test_keyboard_type_rejects_empty_text() -> None:
    result = KeyboardTypeTool().execute({}, None)
    assert result.success is False
    assert result.error == "text is required"


def test_keyboard_press_rejects_missing_keys() -> None:
    result = KeyboardPressTool().execute({}, None)
    assert result.success is False
    assert result.error == "keys must be a non-empty list"


def test_mouse_move_rejects_invalid_coordinates() -> None:
    result = MouseMoveTool().execute({"x": "bad", "y": 10}, None)
    assert result.success is False


def test_mouse_click_rejects_invalid_arguments() -> None:
    result = MouseClickTool().execute({"clicks": "bad"}, None)
    assert result.success is False


def test_mouse_scroll_rejects_invalid_amount() -> None:
    result = MouseScrollTool().execute({"clicks": "bad"}, None)
    assert result.success is False


def test_screenshot_has_default_path_contract() -> None:
    assert ScreenshotTool.name == "take_screenshot"

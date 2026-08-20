"""Keyboard, mouse, and screenshot tools for SATURN on Windows."""

from __future__ import annotations

from typing import Any

from .base import Tool, ToolContext, ToolResult

try:
    import pyautogui
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    pyautogui = None


def _require_pyautogui() -> str | None:
    if pyautogui is None:
        return "pyautogui is not installed"
    return None


class MouseMoveTool(Tool):
    name = "mouse_move"
    description = "Move the mouse cursor to screen coordinates."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        error = _require_pyautogui()
        if error:
            return ToolResult(False, error=error)
        try:
            pyautogui.moveTo(int(arguments["x"]), int(arguments["y"]), duration=0.1)
            return ToolResult(True, output="Mouse moved")
        except (KeyError, TypeError, ValueError) as exc:
            return ToolResult(False, error=f"Invalid coordinates: {exc}")


class MouseClickTool(Tool):
    name = "mouse_click"
    description = "Click the mouse at optional screen coordinates."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        error = _require_pyautogui()
        if error:
            return ToolResult(False, error=error)
        try:
            x = arguments.get("x")
            y = arguments.get("y")
            clicks = int(arguments.get("clicks", 1))
            button = str(arguments.get("button", "left"))
            pyautogui.click(x=None if x is None else int(x), y=None if y is None else int(y), clicks=clicks, button=button)
            return ToolResult(True, output="Mouse clicked")
        except (TypeError, ValueError) as exc:
            return ToolResult(False, error=f"Invalid click arguments: {exc}")


class MouseScrollTool(Tool):
    name = "mouse_scroll"
    description = "Scroll the mouse wheel."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        error = _require_pyautogui()
        if error:
            return ToolResult(False, error=error)
        try:
            pyautogui.scroll(int(arguments.get("clicks", 0)))
            return ToolResult(True, output="Mouse scrolled")
        except (TypeError, ValueError) as exc:
            return ToolResult(False, error=f"Invalid scroll amount: {exc}")


class KeyboardTypeTool(Tool):
    name = "keyboard_type"
    description = "Type text using the keyboard."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        error = _require_pyautogui()
        if error:
            return ToolResult(False, error=error)
        text = str(arguments.get("text", ""))
        if not text:
            return ToolResult(False, error="text is required")
        pyautogui.write(text, interval=float(arguments.get("interval", 0.01)))
        return ToolResult(True, output="Text typed")


class KeyboardPressTool(Tool):
    name = "keyboard_press"
    description = "Press a keyboard key or key combination."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        error = _require_pyautogui()
        if error:
            return ToolResult(False, error=error)
        keys = arguments.get("keys")
        if isinstance(keys, str):
            keys = [keys]
        if not isinstance(keys, list) or not keys:
            return ToolResult(False, error="keys must be a non-empty list")
        try:
            if len(keys) == 1:
                pyautogui.press(str(keys[0]))
            else:
                pyautogui.hotkey(*(str(key) for key in keys))
            return ToolResult(True, output="Key pressed")
        except Exception as exc:
            return ToolResult(False, error=f"Could not press key: {exc}")


class ScreenshotTool(Tool):
    name = "take_screenshot"
    description = "Capture the current screen and save it as a PNG file."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        error = _require_pyautogui()
        if error:
            return ToolResult(False, error=error)
        path = str(arguments.get("path", "saturn_screenshot.png"))
        try:
            image = pyautogui.screenshot()
            image.save(path)
            return ToolResult(True, output=path)
        except Exception as exc:
            return ToolResult(False, error=f"Could not take screenshot: {exc}")


class DesktopToolSet:
    @staticmethod
    def create() -> tuple[Tool, ...]:
        return (
            MouseMoveTool(),
            MouseClickTool(),
            MouseScrollTool(),
            KeyboardTypeTool(),
            KeyboardPressTool(),
            ScreenshotTool(),
        )

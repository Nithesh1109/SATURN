"""Validation and safety policy for SATURN tool actions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    allowed: bool
    error: str | None = None


class ActionValidator:
    """Validate tool names and arguments before they reach the executor."""

    _REQUIRED: dict[str, tuple[str, ...]] = {
        "open_application": ("application",),
        "create_folder": ("path",),
        "create_file": ("path",),
        "copy_file": ("source", "destination"),
        "move_file": ("source", "destination"),
        "delete_file": ("path",),
        "mouse_move": ("x", "y"),
        "keyboard_type": ("text",),
        "keyboard_press": ("keys",),
    }

    _CONFIRMATION_REQUIRED = {"close_application", "lock_computer", "shutdown_computer"}

    def validate(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ValidationResult:
        if not tool_name.strip():
            return ValidationResult(False, "Tool name is required")
        if not isinstance(arguments, dict):
            return ValidationResult(False, "Tool arguments must be an object")

        required = self._REQUIRED.get(tool_name, ())
        missing = [key for key in required if key not in arguments]
        if missing:
            return ValidationResult(False, f"Missing required arguments: {', '.join(missing)}")

        if tool_name in {"mouse_move", "mouse_click"}:
            for key in ("x", "y"):
                if key in arguments:
                    try:
                        value = int(arguments[key])
                    except (TypeError, ValueError):
                        return ValidationResult(False, f"{key} must be an integer")
                    if value < 0:
                        return ValidationResult(False, f"{key} cannot be negative")

        if tool_name == "keyboard_type" and not str(arguments.get("text", "")):
            return ValidationResult(False, "text cannot be empty")

        if tool_name in self._CONFIRMATION_REQUIRED and arguments.get("confirmation") is not True:
            return ValidationResult(False, f"{tool_name} requires confirmation=true")

        return ValidationResult(True)

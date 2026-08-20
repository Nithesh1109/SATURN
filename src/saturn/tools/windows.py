"""Safe Windows desktop tools for SATURN."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from .base import Tool, ToolContext, ToolResult


class OpenApplicationTool(Tool):
    name = "open_application"
    description = "Open a Windows application by executable name or path."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        target = str(arguments.get("application", "")).strip()
        if not target:
            return ToolResult(False, error="application is required")
        try:
            subprocess.Popen([target], shell=False)
            return ToolResult(True, output=f"Opened {target}")
        except (OSError, ValueError) as exc:
            return ToolResult(False, error=f"Could not open application: {exc}")


class CreateFolderTool(Tool):
    name = "create_folder"
    description = "Create a folder at a requested filesystem path."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        raw_path = str(arguments.get("path", "")).strip()
        if not raw_path:
            return ToolResult(False, error="path is required")
        try:
            path = Path(raw_path).expanduser()
            path.mkdir(parents=True, exist_ok=True)
            return ToolResult(True, output=str(path.resolve()))
        except OSError as exc:
            return ToolResult(False, error=f"Could not create folder: {exc}")


class CreateFileTool(Tool):
    name = "create_file"
    description = "Create or overwrite a UTF-8 text file at a requested path."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        raw_path = str(arguments.get("path", "")).strip()
        if not raw_path:
            return ToolResult(False, error="path is required")
        content = str(arguments.get("content", ""))
        try:
            path = Path(raw_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return ToolResult(True, output=str(path.resolve()))
        except OSError as exc:
            return ToolResult(False, error=f"Could not create file: {exc}")


class GetClipboardTool(Tool):
    name = "get_clipboard"
    description = "Read the current Windows text clipboard."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            try:
                value = root.clipboard_get()
            finally:
                root.destroy()
            return ToolResult(True, output=value)
        except Exception as exc:
            return ToolResult(False, error=f"Could not read clipboard: {exc}")


class WindowsToolSet:
    """Factory for the initial low-risk Windows tools."""

    @staticmethod
    def create() -> tuple[Tool, ...]:
        return (
            OpenApplicationTool(),
            CreateFolderTool(),
            CreateFileTool(),
            GetClipboardTool(),
        )

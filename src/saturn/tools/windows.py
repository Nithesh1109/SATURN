"""Windows desktop tools for SATURN."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .base import Tool, ToolContext, ToolResult


def _required(arguments: dict[str, Any], key: str) -> str:
    return str(arguments.get(key, "")).strip()


class OpenApplicationTool(Tool):
    name = "open_application"
    description = "Open a Windows application by executable name or path."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        target = _required(arguments, "application")
        if not target:
            return ToolResult(False, error="application is required")
        try:
            subprocess.Popen([target], shell=False)
            return ToolResult(True, output=f"Opened {target}")
        except (OSError, ValueError) as exc:
            return ToolResult(False, error=f"Could not open application: {exc}")


class CloseApplicationTool(Tool):
    name = "close_application"
    description = "Close a Windows application by process image name."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        target = _required(arguments, "application")
        if not target:
            return ToolResult(False, error="application is required")
        image = Path(target).name
        if not image.lower().endswith(".exe"):
            image += ".exe"
        try:
            completed = subprocess.run(
                ["taskkill", "/IM", image, "/T"],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                return ToolResult(False, error=completed.stderr.strip() or f"Process not found: {image}")
            return ToolResult(True, output=f"Closed {image}")
        except OSError as exc:
            return ToolResult(False, error=f"Could not close application: {exc}")


class CreateFolderTool(Tool):
    name = "create_folder"
    description = "Create a folder at a requested filesystem path."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        raw_path = _required(arguments, "path")
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
        raw_path = _required(arguments, "path")
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


class CopyFileTool(Tool):
    name = "copy_file"
    description = "Copy a file or directory to a destination path."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        source = _required(arguments, "source")
        destination = _required(arguments, "destination")
        if not source or not destination:
            return ToolResult(False, error="source and destination are required")
        try:
            src = Path(source).expanduser()
            dst = Path(destination).expanduser()
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            return ToolResult(True, output=str(dst.resolve()))
        except OSError as exc:
            return ToolResult(False, error=f"Could not copy: {exc}")


class MoveFileTool(Tool):
    name = "move_file"
    description = "Move a file or directory to a destination path."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        source = _required(arguments, "source")
        destination = _required(arguments, "destination")
        if not source or not destination:
            return ToolResult(False, error="source and destination are required")
        try:
            dst = Path(destination).expanduser()
            dst.parent.mkdir(parents=True, exist_ok=True)
            result = shutil.move(str(Path(source).expanduser()), str(dst))
            return ToolResult(True, output=str(Path(result).resolve()))
        except OSError as exc:
            return ToolResult(False, error=f"Could not move: {exc}")


class DeleteFileTool(Tool):
    name = "delete_file"
    description = "Delete a file or an empty directory."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        raw_path = _required(arguments, "path")
        if not raw_path:
            return ToolResult(False, error="path is required")
        try:
            path = Path(raw_path).expanduser()
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()
            return ToolResult(True, output=f"Deleted {path}")
        except OSError as exc:
            return ToolResult(False, error=f"Could not delete: {exc}")


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


class LockComputerTool(Tool):
    name = "lock_computer"
    description = "Lock the current Windows session."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        try:
            result = subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
            if result.returncode != 0:
                return ToolResult(False, error="Windows refused the lock request")
            return ToolResult(True, output="Computer locked")
        except OSError as exc:
            return ToolResult(False, error=f"Could not lock computer: {exc}")


class ShutdownComputerTool(Tool):
    name = "shutdown_computer"
    description = "Shut down Windows. Requires explicit confirmation=true."

    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        if arguments.get("confirmation") is not True:
            return ToolResult(False, error="Explicit confirmation=true is required")
        try:
            subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
            return ToolResult(True, output="Shutdown requested")
        except OSError as exc:
            return ToolResult(False, error=f"Could not request shutdown: {exc}")


class WindowsToolSet:
    """Factory for SATURN's Windows tools."""

    @staticmethod
    def create() -> tuple[Tool, ...]:
        return (
            OpenApplicationTool(),
            CloseApplicationTool(),
            CreateFolderTool(),
            CreateFileTool(),
            CopyFileTool(),
            MoveFileTool(),
            DeleteFileTool(),
            GetClipboardTool(),
            LockComputerTool(),
            ShutdownComputerTool(),
        )

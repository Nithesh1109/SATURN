"""Agent-facing tool execution."""

from __future__ import annotations

from .tool_registry import ToolRegistry
from ..tools.base import ToolContext, ToolResult


class ToolExecutor:
    """Resolve and execute registered tools."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, object],
        context: ToolContext,
    ) -> ToolResult:
        tool = self._registry.get(tool_name)
        if tool is None:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")
        try:
            return tool.execute(arguments, context)
        except Exception as exc:  # Tool boundary: normalize unexpected failures.
            return ToolResult(success=False, error=f"Tool execution failed: {exc}")

    def catalog(self) -> tuple[dict[str, str], ...]:
        """Return registered tool names and descriptions for the planner."""
        return self._registry.catalog()

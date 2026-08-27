"""Agent-facing tool execution."""

from __future__ import annotations

from .tool_registry import ToolRegistry
from ..security.policy import PermissionEngine
from ..tools.base import ToolContext, ToolResult
from ..tools.validator import ActionValidator


class ToolExecutor:
    """Resolve, validate, authorize, and execute registered tools."""

    def __init__(
        self,
        registry: ToolRegistry,
        validator: ActionValidator | None = None,
        permission_engine: PermissionEngine | None = None,
    ) -> None:
        self._registry = registry
        self._validator = validator or ActionValidator()
        self._permissions = permission_engine or PermissionEngine()

    def execute(self, tool_name: str, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        tool = self._registry.get(tool_name)
        if tool is None:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")

        validation = self._validator.validate(tool_name, arguments)
        if not validation.allowed:
            return ToolResult(success=False, error=f"Action rejected: {validation.error}")

        permission = self._permissions.decide(tool_name, arguments)
        if not permission.allowed:
            return ToolResult(success=False, error=f"Permission denied: {permission.reason}")

        try:
            return tool.execute(arguments, context)
        except Exception as exc:
            return ToolResult(success=False, error=f"Tool execution failed: {exc}")

    def catalog(self) -> tuple[dict[str, str], ...]:
        """Return registered tool names and descriptions for the planner."""
        return self._registry.catalog()

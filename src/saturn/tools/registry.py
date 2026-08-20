"""Tool registry and safe lookup."""

from __future__ import annotations

from .base import Tool


class ToolRegistry:
    """In-memory registry of available SATURN tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def catalog(self) -> tuple[dict[str, str], ...]:
        """Return the minimal tool catalog that can be shown to the cloud planner."""
        return tuple(
            {"name": tool.name, "description": tool.description}
            for tool in sorted(self._tools.values(), key=lambda item: item.name)
        )

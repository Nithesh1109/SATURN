"""Tool contracts for SATURN agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..security.permissions import RiskLevel


@dataclass(frozen=True)
class ToolContext:
    """Execution context supplied to a tool."""

    request_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    """Normalized result returned by a tool."""

    success: bool
    output: Any = None
    error: str | None = None


class Tool(ABC):
    """Base contract every SATURN tool must implement.

    Tools may declare their risk explicitly. SATURN's central permission engine
    still overrides this declaration for built-in security-sensitive tools.
    """

    name: str
    description: str
    risk_level: RiskLevel = RiskLevel.LOW

    @abstractmethod
    def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        raise NotImplementedError

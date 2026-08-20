"""Permission primitives for SATURN tool execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PermissionPolicy:
    """Policy describing what a tool invocation is allowed to do."""

    risk: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
    allowed: bool = True

    def allows(self) -> bool:
        return self.allowed

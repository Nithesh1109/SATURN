"""Agent planning contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlanStep:
    """One planned action before execution."""

    action: str
    arguments: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass(frozen=True)
class AgentPlan:
    """Execution plan produced from a user request."""

    goal: str
    steps: tuple[PlanStep, ...] = ()

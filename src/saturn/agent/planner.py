"""Agent planning contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from saturn.ai.providers import AIResponse


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


class Planner(ABC):
    """Contract for components that produce executable plans."""

    @abstractmethod
    def create_plan(self, goal: str, ai_response: AIResponse | None = None) -> AgentPlan:
        raise NotImplementedError


class RuleBasedPlanner(Planner):
    """Reads structured plan metadata and emits deterministic execution steps."""

    def create_plan(self, goal: str, ai_response: AIResponse | None = None) -> AgentPlan:
        if ai_response is None:
            return AgentPlan(goal=goal)

        raw_steps = ai_response.metadata.get("tool_calls", [])
        steps: list[PlanStep] = []
        if isinstance(raw_steps, list):
            for raw_step in raw_steps:
                if not isinstance(raw_step, dict):
                    continue
                tool_name = str(raw_step.get("name", "")).strip()
                if not tool_name:
                    continue
                arguments = raw_step.get("arguments", {})
                if not isinstance(arguments, dict):
                    arguments = {}
                reason = str(raw_step.get("reason", ""))
                steps.append(PlanStep(action=tool_name, arguments=arguments, reason=reason))
        return AgentPlan(goal=goal, steps=tuple(steps))

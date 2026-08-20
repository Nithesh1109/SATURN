"""Agent planning contracts and cloud-model plan parsing."""

from __future__ import annotations

import json
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
    """Convert the cloud model's structured action output into executable steps.

    The cloud provider deliberately remains provider-agnostic. The model is asked
    to return a small JSON object containing ``tool_calls``; this planner accepts
    that metadata directly and also parses the same structure from ``AIResponse.text``
    so mocked providers and OpenAI-compatible endpoints behave consistently.
    """

    PLAN_SYSTEM_PROMPT = (
        "You are SATURN's action planner. Decide which registered tools are needed "
        "to accomplish the user's request. Return ONLY valid JSON in this shape: "
        '{"response":"brief user-facing response","tool_calls":['
        '{"name":"tool_name","arguments":{},"reason":"why"}]}. '
        "If no tool is needed, return an empty tool_calls array. Never invent tool "
        "results or claim an action was executed."
    )

    def create_plan(self, goal: str, ai_response: AIResponse | None = None) -> AgentPlan:
        if ai_response is None:
            return AgentPlan(goal=goal)

        raw_steps = ai_response.metadata.get("tool_calls")
        if raw_steps is None:
            payload = self._parse_json(ai_response.text)
            if payload is not None:
                raw_steps = payload.get("tool_calls", payload.get("steps", []))

        steps: list[PlanStep] = []
        if isinstance(raw_steps, list):
            for raw_step in raw_steps:
                if not isinstance(raw_step, dict):
                    continue
                tool_name = str(raw_step.get("name", raw_step.get("action", ""))).strip()
                if not tool_name:
                    continue
                arguments = raw_step.get("arguments", {})
                if not isinstance(arguments, dict):
                    arguments = {}
                reason = str(raw_step.get("reason", ""))
                steps.append(PlanStep(action=tool_name, arguments=arguments, reason=reason))

        return AgentPlan(goal=goal, steps=tuple(steps))

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any] | None:
        """Parse a JSON object, tolerating a surrounding markdown code fence."""
        candidate = text.strip()
        if not candidate:
            return None
        if candidate.startswith("```"):
            lines = candidate.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            candidate = "\n".join(lines).strip()
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None

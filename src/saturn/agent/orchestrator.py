"""Agent orchestration wiring for Router -> Agent -> Planner -> ToolExecutor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from saturn.ai.providers import AIRequest, AIResponse
from saturn.ai.router import AIRouter
from saturn.tools.base import ToolContext, ToolResult

from .executor import ToolExecutor
from .planner import AgentPlan, PlanStep, Planner
from .session import AgentSession


@dataclass(frozen=True)
class StepExecution:
    """One executed plan step and its normalized result."""

    step: PlanStep
    result: ToolResult


@dataclass(frozen=True)
class AgentRunResult:
    """Execution artifact returned by SATURN's agent layer."""

    response: AIResponse
    plan: AgentPlan
    executions: tuple[StepExecution, ...]

    @property
    def success(self) -> bool:
        return all(execution.result.success for execution in self.executions)


class SaturnAgent:
    """Coordinates AI response, planning, and tool execution for one request."""

    def __init__(self, router: AIRouter, planner: Planner, executor: ToolExecutor) -> None:
        self._router = router
        self._planner = planner
        self._executor = executor

    def run(self, request: AIRequest, context: ToolContext | None = None) -> AgentRunResult:
        response = self._router.generate(request)
        plan = self._planner.create_plan(goal=request.prompt, ai_response=response)
        tool_context = context or ToolContext()

        executions: list[StepExecution] = []
        for step in plan.steps:
            result = self._executor.execute(step.action, step.arguments, tool_context)
            executions.append(StepExecution(step=step, result=result))

        return AgentRunResult(response=response, plan=plan, executions=tuple(executions))


class TaskOrchestrator:
    """Entry point for executing a user goal through the SATURN agent pipeline."""

    def __init__(self, agent: SaturnAgent) -> None:
        self._agent = agent

    def run(
        self,
        goal: str,
        *,
        session: AgentSession | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentRunResult:
        context = session.history if session is not None else []
        request = AIRequest(prompt=goal, context=self._normalize_context(context), metadata=metadata or {})
        result = self._agent.run(request, context=ToolContext(metadata={"goal": goal}))

        if session is not None:
            session.add("user", goal)
            session.add("assistant", result.response.text)
        return result

    def _normalize_context(self, context: list[dict[str, Any]]) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for entry in context:
            role = str(entry.get("role", "user"))
            content = str(entry.get("content", ""))
            normalized.append({"role": role, "content": content})
        return normalized

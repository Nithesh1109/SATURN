"""Agent orchestration wiring for Router -> Agent -> Planner -> ToolExecutor."""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from saturn.ai.providers import AIRequest, AIResponse
from saturn.ai.router import AIRouter
from saturn.tools.base import ToolContext, ToolResult

from .executor import ToolExecutor
from .planner import AgentPlan, PlanStep, Planner, RuleBasedPlanner
from .session import AgentSession


class TaskLifecycleState(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class CancellationToken:
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True


class ResultVerifier(ABC):
    @abstractmethod
    def verify(self, step: PlanStep, result: ToolResult, context: ToolContext) -> bool:
        raise NotImplementedError


class DefaultResultVerifier(ResultVerifier):
    def verify(self, step: PlanStep, result: ToolResult, context: ToolContext) -> bool:
        return result.success


@dataclass(frozen=True)
class StepExecution:
    step: PlanStep
    result: ToolResult
    attempt: int = 1
    verified: bool = True


@dataclass(frozen=True)
class AgentRunResult:
    task_id: str
    goal: str
    response: AIResponse
    plan: AgentPlan
    executions: tuple[StepExecution, ...]
    state: TaskLifecycleState
    lifecycle: tuple[TaskLifecycleState, ...]
    error: str | None = None
    cancelled: bool = False
    timed_out: bool = False

    @property
    def success(self) -> bool:
        if self.state is not TaskLifecycleState.COMPLETED:
            return False
        return all(execution.result.success and execution.verified for execution in self.executions)


class AgentOrchestrator:
    """Manage planning, execution, verification, and feedback-driven replanning."""

    def __init__(
        self,
        router: AIRouter,
        planner: Planner,
        executor: ToolExecutor,
        *,
        verifier: ResultVerifier | None = None,
        max_step_retries: int = 0,
        max_replans: int = 0,
    ) -> None:
        self._router = router
        self._planner = planner
        self._executor = executor
        self._verifier = verifier or DefaultResultVerifier()
        self._max_step_retries = max(0, max_step_retries)
        self._max_replans = max(0, max_replans)

    def run(
        self,
        request: AIRequest,
        *,
        context: ToolContext | None = None,
        cancellation_token: CancellationToken | None = None,
        timeout_seconds: float | None = None,
        max_step_retries: int | None = None,
        max_replans: int | None = None,
        task_id: str | None = None,
    ) -> AgentRunResult:
        started_at = time.monotonic()
        tool_context = context or ToolContext()
        lifecycle: list[TaskLifecycleState] = [TaskLifecycleState.PENDING]
        state = TaskLifecycleState.PENDING
        response = AIResponse(text="", provider="none", model="none", metadata={"mode": "not_run"})
        plan = AgentPlan(goal=request.prompt)
        executions: list[StepExecution] = []
        feedback: list[dict[str, Any]] = []
        retries = self._max_step_retries if max_step_retries is None else max(0, max_step_retries)
        replans_left = self._max_replans if max_replans is None else max(0, max_replans)
        identifier = task_id or str(uuid.uuid4())

        def set_state(next_state: TaskLifecycleState) -> None:
            nonlocal state
            if lifecycle[-1] is not next_state:
                lifecycle.append(next_state)
            state = next_state

        def timed_out() -> bool:
            return timeout_seconds is not None and (time.monotonic() - started_at) >= timeout_seconds

        def finalize(final_state: TaskLifecycleState, *, error: str | None = None, cancelled: bool = False, timeout: bool = False) -> AgentRunResult:
            set_state(final_state)
            return AgentRunResult(
                task_id=identifier,
                goal=request.prompt,
                response=response,
                plan=plan,
                executions=tuple(executions),
                state=state,
                lifecycle=tuple(lifecycle),
                error=error,
                cancelled=cancelled,
                timed_out=timeout,
            )

        if cancellation_token is not None and cancellation_token.cancelled:
            return finalize(TaskLifecycleState.CANCELLED, error="Task cancelled before planning", cancelled=True)
        if timed_out():
            return finalize(TaskLifecycleState.FAILED, error="Task timed out before planning", timeout=True)

        set_state(TaskLifecycleState.PLANNING)
        planning_request = self._build_planning_request(request, feedback=feedback)
        response = self._router.generate(planning_request)
        plan = self._planner.create_plan(goal=request.prompt, ai_response=response)
        current_plan = plan

        while True:
            replan_needed = False

            for step in current_plan.steps:
                if cancellation_token is not None and cancellation_token.cancelled:
                    return finalize(TaskLifecycleState.CANCELLED, error="Task cancelled", cancelled=True)
                if timed_out():
                    return finalize(TaskLifecycleState.FAILED, error="Task timed out", timeout=True)

                for attempt in range(1, retries + 2):
                    set_state(TaskLifecycleState.EXECUTING)
                    observed = self._executor.execute(step.action, step.arguments, tool_context)
                    set_state(TaskLifecycleState.VERIFYING)
                    verified = self._verifier.verify(step, observed, tool_context)
                    executions.append(StepExecution(step=step, result=observed, attempt=attempt, verified=verified))
                    feedback.append(self._build_execution_feedback(step, observed, verified, attempt))

                    if cancellation_token is not None and cancellation_token.cancelled:
                        return finalize(TaskLifecycleState.CANCELLED, error="Task cancelled", cancelled=True)
                    if timed_out():
                        return finalize(TaskLifecycleState.FAILED, error="Task timed out", timeout=True)

                    if verified:
                        break
                    if attempt <= retries:
                        continue
                    if replans_left > 0:
                        replans_left -= 1
                        set_state(TaskLifecycleState.PLANNING)
                        planning_request = self._build_planning_request(request, feedback=feedback)
                        response = self._router.generate(planning_request)
                        current_plan = self._planner.create_plan(goal=request.prompt, ai_response=response)
                        replan_needed = True
                        break

                    failure = observed.error or f"Step execution failed for tool '{step.action}'"
                    return finalize(TaskLifecycleState.FAILED, error=failure)

                if replan_needed:
                    break

            if replan_needed:
                continue
            break

        return finalize(TaskLifecycleState.COMPLETED)

    def _build_execution_feedback(self, step: PlanStep, result: ToolResult, verified: bool, attempt: int) -> dict[str, Any]:
        return {
            "tool": step.action,
            "arguments": dict(step.arguments),
            "attempt": attempt,
            "success": result.success,
            "verified": verified,
            "output": result.output,
            "error": result.error,
        }

    def _build_planning_request(self, request: AIRequest, *, feedback: list[dict[str, Any]] | None = None) -> AIRequest:
        catalog = self._executor.catalog()
        tool_lines = [f"- {item['name']}: {item['description']}" for item in catalog if item.get("name") and item.get("description")]
        tools_text = "\n".join(tool_lines) if tool_lines else "- No tools are currently registered."
        system = request.system or RuleBasedPlanner.PLAN_SYSTEM_PROMPT
        system = f"{system}\n\nAvailable SATURN tools:\n{tools_text}"
        context = list(request.context)
        if feedback:
            context.append({"role": "system", "content": "Observed SATURN tool results. Use these results when correcting or continuing the plan."})
            for item in feedback:
                context.append({"role": "tool", "content": str(item)})
        return AIRequest(
            prompt=request.prompt,
            system=system,
            context=context,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            metadata={**request.metadata, "mode": "cloud_planning", "feedback_count": len(feedback or [])},
        )


class SaturnAgent:
    def __init__(self, router: AIRouter, planner: Planner, executor: ToolExecutor, *, verifier: ResultVerifier | None = None, max_step_retries: int = 0, max_replans: int = 0) -> None:
        self._orchestrator = AgentOrchestrator(router=router, planner=planner, executor=executor, verifier=verifier, max_step_retries=max_step_retries, max_replans=max_replans)

    def run(self, request: AIRequest, context: ToolContext | None = None, *, cancellation_token: CancellationToken | None = None, timeout_seconds: float | None = None) -> AgentRunResult:
        return self._orchestrator.run(request, context=context, cancellation_token=cancellation_token, timeout_seconds=timeout_seconds)


class TaskOrchestrator:
    def __init__(self, agent: SaturnAgent | AgentOrchestrator) -> None:
        self._agent = agent

    def run(self, goal: str, *, session: AgentSession | None = None, metadata: dict[str, Any] | None = None, cancellation_token: CancellationToken | None = None, timeout_seconds: float | None = None) -> AgentRunResult:
        context = session.history if session is not None else []
        request = AIRequest(prompt=goal, context=self._normalize_context(context), metadata=metadata or {})
        result = self._agent.run(request, context=ToolContext(metadata={"goal": goal}), cancellation_token=cancellation_token, timeout_seconds=timeout_seconds)
        if session is not None:
            session.add("user", goal)
            session.add("assistant", result.response.text)
        return result

    def _normalize_context(self, context: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [{"role": str(entry.get("role", "user")), "content": str(entry.get("content", ""))} for entry in context]

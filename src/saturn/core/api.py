"""Local API contract for the SATURN core."""

from __future__ import annotations

from dataclasses import asdict

from saturn.agent.executor import ToolExecutor
from saturn.agent.orchestrator import TaskOrchestrator
from saturn.agent.planner import RuleBasedPlanner
from saturn.ai.cloud_provider import CloudAIProvider
from saturn.ai.local_provider import LocalAIProvider
from saturn.ai.router import AIRouter
from saturn.tools.registry import ToolRegistry

from .runtime import SaturnCore


class CoreAPI:
    """Application-facing interface to the SATURN core runtime."""

    def __init__(
        self,
        core: SaturnCore | None = None,
        orchestrator: TaskOrchestrator | None = None,
    ) -> None:
        self._core = core or SaturnCore()
        self._orchestrator = orchestrator or self._build_default_orchestrator()

    def health(self) -> dict[str, object]:
        """Return a serializable health/status payload."""
        return asdict(self._core.status())

    def start(self) -> dict[str, object]:
        """Start the core and return its status."""
        return asdict(self._core.start())

    def stop(self) -> dict[str, object]:
        """Stop the core and return its status."""
        return asdict(self._core.stop())

    def run_task(self, goal: str) -> dict[str, object]:
        """Execute a goal through Router -> Agent -> Planner -> ToolExecutor."""
        result = self._orchestrator.run(goal)
        return {
            "response": asdict(result.response),
            "plan": asdict(result.plan),
            "executions": [asdict(execution) for execution in result.executions],
            "success": result.success,
        }

    def _build_default_orchestrator(self) -> TaskOrchestrator:
        local = LocalAIProvider()
        cloud = CloudAIProvider()
        router = AIRouter(local=local, cloud=cloud)
        planner = RuleBasedPlanner()
        executor = ToolExecutor(ToolRegistry())
        from saturn.agent.orchestrator import SaturnAgent

        return TaskOrchestrator(SaturnAgent(router=router, planner=planner, executor=executor))

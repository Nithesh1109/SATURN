import time

from saturn.agent.executor import ToolExecutor
from saturn.agent.orchestrator import CancellationToken, SaturnAgent, TaskLifecycleState, TaskOrchestrator
from saturn.agent.planner import AgentPlan, PlanStep, Planner, RuleBasedPlanner
from saturn.ai.providers import AIProvider, AIRequest, AIResponse
from saturn.ai.router import AIRouter
from saturn.tools.base import Tool, ToolContext, ToolResult
from saturn.tools.registry import ToolRegistry


class PlanningProvider(AIProvider):
    name = "cloud-test"

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            text="planned",
            provider=self.name,
            model="fake-model",
            metadata={
                "tool_calls": [
                    {
                        "name": "echo",
                        "arguments": {"message": request.prompt},
                        "reason": "confirm goal",
                    }
                ],
            },
        )


class EchoTool(Tool):
    name = "echo"
    description = "Echo test payload."

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        return ToolResult(success=True, output=arguments.get("message"))


class FlakyTool(Tool):
    name = "flaky"
    description = "Fails once then succeeds."

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        self.calls += 1
        if self.calls == 1:
            return ToolResult(success=False, error="transient")
        return ToolResult(success=True, output="recovered")


class AlwaysFailTool(Tool):
    name = "fail"
    description = "Always fails."

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        return ToolResult(success=False, error="boom")


class SlowTool(Tool):
    name = "slow"
    description = "Sleeps to trigger timeout."

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        time.sleep(0.02)
        return ToolResult(success=True, output="done")


class StaticPlanner(Planner):
    def __init__(self, plans: list[AgentPlan]) -> None:
        self._plans = plans
        self._calls = 0

    def create_plan(self, goal: str, ai_response: AIResponse | None = None) -> AgentPlan:
        index = min(self._calls, len(self._plans) - 1)
        self._calls += 1
        return self._plans[index]


def build_registry(*tools: Tool) -> ToolRegistry:
    registry = ToolRegistry()
    for tool in tools:
        registry.register(tool)
    return registry


def build_router(provider: AIProvider) -> AIRouter:
    return AIRouter(cloud=provider)


def test_orchestrator_runs_router_to_executor_pipeline() -> None:
    registry = build_registry(EchoTool())

    agent = SaturnAgent(
        router=build_router(PlanningProvider()),
        planner=RuleBasedPlanner(),
        executor=ToolExecutor(registry),
    )
    orchestrator = TaskOrchestrator(agent)

    result = orchestrator.run("ship foundation")

    assert result.response.text == "planned"
    assert result.success is True
    assert result.state is TaskLifecycleState.COMPLETED
    assert len(result.plan.steps) == 1
    assert result.executions[0].result.output == "ship foundation"
    assert result.executions[0].verified is True


def test_orchestrator_retries_failed_tool_safely() -> None:
    flaky = FlakyTool()
    registry = build_registry(flaky)

    response = AIResponse(
        text="planned",
        provider="cloud-test",
        model="fake",
        metadata={"tool_calls": [{"name": "flaky", "arguments": {}}]},
    )

    class Provider(AIProvider):
        name = "cloud-test"

        def generate(self, request: AIRequest) -> AIResponse:
            return response

    agent = SaturnAgent(
        router=build_router(Provider()),
        planner=RuleBasedPlanner(),
        executor=ToolExecutor(registry),
        max_step_retries=1,
    )

    result = TaskOrchestrator(agent).run("recover")

    assert result.state is TaskLifecycleState.COMPLETED
    assert len(result.executions) == 2
    assert result.executions[0].attempt == 1
    assert result.executions[1].attempt == 2


def test_orchestrator_fails_when_retry_budget_exhausted() -> None:
    registry = build_registry(AlwaysFailTool())
    plan = AgentPlan(goal="fail", steps=(PlanStep(action="fail"),))

    class Provider(AIProvider):
        name = "cloud-test"

        def generate(self, request: AIRequest) -> AIResponse:
            return AIResponse(text="planned", provider=self.name, model="fake")

    agent = SaturnAgent(
        router=build_router(Provider()),
        planner=StaticPlanner([plan]),
        executor=ToolExecutor(registry),
        max_step_retries=1,
    )

    result = TaskOrchestrator(agent).run("fail")

    assert result.state is TaskLifecycleState.FAILED
    assert result.success is False
    assert result.error == "boom"
    assert len(result.executions) == 2


def test_orchestrator_replans_after_failed_verification() -> None:
    registry = build_registry(AlwaysFailTool(), EchoTool())
    first = AgentPlan(goal="recover", steps=(PlanStep(action="fail"),))
    second = AgentPlan(goal="recover", steps=(PlanStep(action="echo", arguments={"message": "fixed"}),))

    class Provider(AIProvider):
        name = "cloud-test"

        def generate(self, request: AIRequest) -> AIResponse:
            return AIResponse(text="planned", provider=self.name, model="fake")

    agent = SaturnAgent(
        router=build_router(Provider()),
        planner=StaticPlanner([first, second]),
        executor=ToolExecutor(registry),
        max_replans=1,
    )

    result = TaskOrchestrator(agent).run("recover")

    assert result.state is TaskLifecycleState.COMPLETED
    assert [execution.step.action for execution in result.executions] == ["fail", "echo"]


def test_orchestrator_supports_cancellation() -> None:
    registry = build_registry(EchoTool())
    token = CancellationToken(cancelled=True)

    agent = SaturnAgent(
        router=build_router(PlanningProvider()),
        planner=RuleBasedPlanner(),
        executor=ToolExecutor(registry),
    )

    result = TaskOrchestrator(agent).run("cancel me", cancellation_token=token)

    assert result.state is TaskLifecycleState.CANCELLED
    assert result.cancelled is True
    assert result.executions == ()


def test_orchestrator_enforces_timeout() -> None:
    registry = build_registry(SlowTool())
    plan = AgentPlan(goal="slow", steps=(PlanStep(action="slow"),))

    class Provider(AIProvider):
        name = "cloud-test"

        def generate(self, request: AIRequest) -> AIResponse:
            return AIResponse(text="planned", provider=self.name, model="fake")

    agent = SaturnAgent(
        router=build_router(Provider()),
        planner=StaticPlanner([plan]),
        executor=ToolExecutor(registry),
    )

    result = TaskOrchestrator(agent).run("slow", timeout_seconds=0.001)

    assert result.state is TaskLifecycleState.FAILED
    assert result.timed_out is True

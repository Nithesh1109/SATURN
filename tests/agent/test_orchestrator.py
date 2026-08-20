from saturn.agent.executor import ToolExecutor
from saturn.agent.orchestrator import SaturnAgent, TaskOrchestrator
from saturn.agent.planner import RuleBasedPlanner
from saturn.ai.providers import AIProvider, AIRequest, AIResponse
from saturn.ai.router import AIRouter
from saturn.tools.base import Tool, ToolContext, ToolResult
from saturn.tools.registry import ToolRegistry


class PlanningProvider(AIProvider):
    name = "local"

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
                ]
            },
        )


class EchoTool(Tool):
    name = "echo"
    description = "Echo test payload."

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        return ToolResult(success=True, output=arguments.get("message"))


def test_orchestrator_runs_router_to_executor_pipeline() -> None:
    registry = ToolRegistry()
    registry.register(EchoTool())

    agent = SaturnAgent(
        router=AIRouter(local=PlanningProvider()),
        planner=RuleBasedPlanner(),
        executor=ToolExecutor(registry),
    )
    orchestrator = TaskOrchestrator(agent)

    result = orchestrator.run("ship foundation")

    assert result.response.text == "planned"
    assert result.success is True
    assert len(result.plan.steps) == 1
    assert result.executions[0].result.output == "ship foundation"

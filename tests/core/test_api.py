from saturn.agent.executor import ToolExecutor
from saturn.agent.orchestrator import SaturnAgent, TaskOrchestrator
from saturn.agent.planner import RuleBasedPlanner
from saturn.ai.cloud_provider import CloudAIProvider
from saturn.ai.providers import AIRequest, AIResponse
from saturn.ai.router import AIRouter
from saturn.core.api import CoreAPI
from saturn.tools.base import Tool, ToolContext, ToolResult
from saturn.tools.registry import ToolRegistry


class EchoTool(Tool):
    name = "echo"
    description = "Echo test payload."

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        return ToolResult(success=True, output=arguments.get("message"))


def build_test_api() -> CoreAPI:
    def responder(request: AIRequest) -> AIResponse:
        return AIResponse(
            text="planned",
            provider="cloud-test",
            model="fake-model",
            metadata={
                "tool_calls": [
                    {"name": "echo", "arguments": {"message": request.prompt}},
                ],
            },
        )

    provider = CloudAIProvider(responder=responder)
    router = AIRouter(cloud=provider)
    registry = ToolRegistry()
    registry.register(EchoTool())
    agent = SaturnAgent(
        router=router,
        planner=RuleBasedPlanner(),
        executor=ToolExecutor(registry),
    )
    return CoreAPI(orchestrator=TaskOrchestrator(agent))


def test_api_starts_and_reports_health() -> None:
    api = CoreAPI()

    assert api.health()["state"] == "offline"

    status = api.start()

    assert status["state"] == "online"
    assert api.health()["state"] == "online"


def test_api_stops_core() -> None:
    api = CoreAPI()
    api.start()

    status = api.stop()

    assert status["state"] == "offline"


def test_api_runs_agent_task() -> None:
    api = build_test_api()

    result = api.run_task("hello saturn")

    assert result["response"]["text"] == "planned"
    assert result["success"] is True

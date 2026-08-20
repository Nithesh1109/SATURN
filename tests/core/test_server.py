import json
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from threading import Thread

from saturn.core.server import CoreRequestHandler
from saturn.core.api import CoreAPI
from saturn.agent.executor import ToolExecutor
from saturn.agent.orchestrator import SaturnAgent, TaskOrchestrator
from saturn.agent.planner import RuleBasedPlanner
from saturn.ai.cloud_provider import CloudAIProvider
from saturn.ai.providers import AIRequest, AIResponse
from saturn.ai.router import AIRouter
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
            metadata={"tool_calls": [{"name": "echo", "arguments": {"message": request.prompt}}]},
        )

    provider = CloudAIProvider(responder=responder)
    router = AIRouter(cloud=provider)
    registry = ToolRegistry()
    registry.register(EchoTool())
    agent = SaturnAgent(router=router, planner=RuleBasedPlanner(), executor=ToolExecutor(registry))
    return CoreAPI(orchestrator=TaskOrchestrator(agent))


def test_health_endpoint() -> None:
    original_api = CoreRequestHandler.api
    CoreRequestHandler.api = CoreAPI()
    server = ThreadingHTTPServer(("127.0.0.1", 0), CoreRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/health")
        response = connection.getresponse()
        payload = json.loads(response.read())
        assert response.status == 200
        assert payload["state"] == "offline"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        CoreRequestHandler.api = original_api


def test_agent_run_endpoint() -> None:
    original_api = CoreRequestHandler.api
    CoreRequestHandler.api = build_test_api()
    server = ThreadingHTTPServer(("127.0.0.1", 0), CoreRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request(
            "POST", "/agent/run", body=json.dumps({"goal": "ping"}),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        payload = json.loads(response.read())
        assert response.status == 200
        assert payload["response"]["text"] == "planned"
        assert payload["success"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        CoreRequestHandler.api = original_api

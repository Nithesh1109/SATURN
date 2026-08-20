from saturn.agent.executor import ToolExecutor
from saturn.tools.base import Tool, ToolContext, ToolResult
from saturn.tools.registry import ToolRegistry


class EchoTool(Tool):
    name = "echo"
    description = "Return the supplied message."

    def execute(self, arguments: dict[str, object], context: ToolContext) -> ToolResult:
        return ToolResult(success=True, output=arguments.get("message"))


def test_executor_runs_registered_tool() -> None:
    registry = ToolRegistry()
    registry.register(EchoTool())
    executor = ToolExecutor(registry)

    result = executor.execute("echo", {"message": "hello"}, ToolContext(request_id="1"))

    assert result.success is True
    assert result.output == "hello"


def test_executor_rejects_unknown_tool() -> None:
    executor = ToolExecutor(ToolRegistry())

    result = executor.execute("missing", {}, ToolContext())

    assert result.success is False
    assert result.error == "Unknown tool: missing"

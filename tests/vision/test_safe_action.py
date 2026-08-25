from saturn.tools.base import ToolContext, ToolResult
from saturn.tools.validator import ActionValidator
from saturn.vision.safe_action import SafeVisionActionExecutor


class FakeExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, tool_name, arguments, context):
        self.calls.append((tool_name, arguments))
        return ToolResult(success=True, output="clicked")


def test_vision_action_passes_through_validator_and_executor() -> None:
    executor = FakeExecutor()
    safe = SafeVisionActionExecutor(executor)
    result = safe.execute(
        tool_name="mouse_move",
        arguments={"x": 100, "y": 200},
        context=ToolContext(),
    )
    assert result.allowed is True
    assert result.result.success is True
    assert executor.calls == [("mouse_move", {"x": 100, "y": 200})]


def test_vision_action_is_rejected_before_executor() -> None:
    executor = FakeExecutor()
    safe = SafeVisionActionExecutor(executor, ActionValidator())
    result = safe.execute(
        tool_name="shutdown_computer",
        arguments={},
        context=ToolContext(),
    )
    assert result.allowed is False
    assert "confirmation=true" in result.error
    assert executor.calls == []

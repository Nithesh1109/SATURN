from saturn.agent.planner import RuleBasedPlanner
from saturn.ai.providers import AIResponse


def test_planner_parses_structured_cloud_response() -> None:
    response = AIResponse(
        text='{"response":"Opening the app","tool_calls":[{"name":"open_app","arguments":{"name":"Chrome"},"reason":"User asked to open Chrome"}]}',
        provider="nvidia-nim",
        model="test-model",
    )

    plan = RuleBasedPlanner().create_plan("Open Chrome", response)

    assert len(plan.steps) == 1
    assert plan.steps[0].action == "open_app"
    assert plan.steps[0].arguments == {"name": "Chrome"}


def test_planner_accepts_markdown_json() -> None:
    response = AIResponse(
        text='```json\n{"tool_calls":[{"name":"echo","arguments":{"text":"hello"}}]}\n```',
        provider="test",
        model="test-model",
    )

    plan = RuleBasedPlanner().create_plan("Say hello", response)

    assert plan.steps[0].action == "echo"

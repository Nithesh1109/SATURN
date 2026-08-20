from saturn.ai.providers import AIProvider, AIRequest, AIResponse
from saturn.ai.router import AIRouter, Route


class FakeProvider(AIProvider):
    def __init__(self, name: str, is_available: bool = True) -> None:
        self.name = name
        self.is_available = is_available

    def available(self) -> bool:
        return self.is_available

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(request.prompt, self.name, "fake")


def test_router_prefers_local() -> None:
    router = AIRouter(FakeProvider("local"), FakeProvider("cloud"))
    decision = router.decide(AIRequest("hello"))

    assert decision.route is Route.LOCAL


def test_router_falls_back_to_cloud() -> None:
    router = AIRouter(FakeProvider("local", False), FakeProvider("cloud"))
    response = router.generate(AIRequest("hello"))

    assert response.provider == "cloud"


def test_router_fails_without_provider() -> None:
    router = AIRouter(FakeProvider("local", False), FakeProvider("cloud", False))

    try:
        router.decide(AIRequest("hello"))
    except RuntimeError as exc:
        assert "No SATURN AI provider" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")

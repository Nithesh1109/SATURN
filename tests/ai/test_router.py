from saturn.ai.providers import AIProvider, AIRequest, AIResponse
from saturn.ai.router import AIRouter, Route


class FakeProvider(AIProvider):
    def __init__(self, name: str = "cloud", is_available: bool = True) -> None:
        self.name = name
        self.is_available = is_available

    def available(self) -> bool:
        return self.is_available

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(request.prompt, self.name, "fake")


def test_router_always_uses_cloud() -> None:
    router = AIRouter(FakeProvider())
    decision = router.decide(AIRequest("hello"))

    assert decision.route is Route.CLOUD
    assert decision.reason == "cloud-first"


def test_router_generates_with_cloud() -> None:
    router = AIRouter(FakeProvider())
    response = router.generate(AIRequest("hello"))

    assert response.provider == "cloud"


def test_router_fails_when_cloud_is_unavailable() -> None:
    router = AIRouter(FakeProvider(is_available=False))

    try:
        router.decide(AIRequest("hello"))
    except RuntimeError as exc:
        assert "cloud AI provider is unavailable" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")

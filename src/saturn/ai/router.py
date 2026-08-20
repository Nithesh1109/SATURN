"""AI routing policy for SATURN's hybrid architecture."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from saturn.router.policy import Provider, RouterPolicy

from .providers import AIProvider, AIRequest, AIResponse, ProviderKind


class Route(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


@dataclass(frozen=True)
class RoutingDecision:
    route: Route
    reason: str


class AIRouter:
    """Select an available provider without coupling SATURN to a vendor."""

    def __init__(
        self,
        local: AIProvider,
        cloud: AIProvider | None = None,
        policy: RouterPolicy | None = None,
    ) -> None:
        self.local = local
        self.cloud = cloud
        self._policy = policy or RouterPolicy()

    def decide(self, request: AIRequest) -> RoutingDecision:
        preferred = request.preferred_route or self._route_from_policy(request.complexity)
        candidates: list[tuple[Route, AIProvider | None]]

        if preferred is ProviderKind.CLOUD:
            candidates = [(Route.CLOUD, self.cloud), (Route.LOCAL, self.local)]
        else:
            candidates = [(Route.LOCAL, self.local), (Route.CLOUD, self.cloud)]

        for route, provider in candidates:
            if provider is not None and provider.available():
                return RoutingDecision(route, f"policy:{preferred.value}")
        raise RuntimeError("No SATURN AI provider is available")

    def generate(self, request: AIRequest) -> AIResponse:
        decision = self.decide(request)
        provider = self.local if decision.route is Route.LOCAL else self.cloud
        assert provider is not None
        return provider.generate(request)

    def _route_from_policy(self, complexity: str) -> ProviderKind:
        decision = self._policy.choose(complexity)
        if decision.provider is Provider.CLOUD:
            return ProviderKind.CLOUD
        return ProviderKind.LOCAL

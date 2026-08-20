"""AI routing policy for SATURN's hybrid architecture."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .providers import AIProvider, AIRequest, AIResponse


class Route(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


@dataclass(frozen=True)
class RoutingDecision:
    route: Route
    reason: str


class AIRouter:
    """Select an available provider without coupling SATURN to a vendor."""

    def __init__(self, local: AIProvider, cloud: AIProvider | None = None) -> None:
        self.local = local
        self.cloud = cloud

    def decide(self, request: AIRequest) -> RoutingDecision:
        # Local is the default for privacy, speed, and offline capability.
        if self.local.available():
            return RoutingDecision(Route.LOCAL, "local-first")
        if self.cloud is not None and self.cloud.available():
            return RoutingDecision(Route.CLOUD, "local-unavailable")
        raise RuntimeError("No SATURN AI provider is available")

    def generate(self, request: AIRequest) -> AIResponse:
        decision = self.decide(request)
        provider = self.local if decision.route is Route.LOCAL else self.cloud
        assert provider is not None
        return provider.generate(request)

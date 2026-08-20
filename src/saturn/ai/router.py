"""Cloud-first AI routing for SATURN v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .providers import AIProvider, AIRequest, AIResponse


class Route(str, Enum):
    """The execution route available to SATURN v1."""

    CLOUD = "cloud"


@dataclass(frozen=True)
class RoutingDecision:
    route: Route
    reason: str


class AIRouter:
    """Keep provider selection simple: SATURN v1 uses its cloud brain."""

    def __init__(self, cloud: AIProvider) -> None:
        self.cloud = cloud

    def decide(self, request: AIRequest | None = None) -> RoutingDecision:
        if not self.cloud.available():
            raise RuntimeError("SATURN cloud AI provider is unavailable")
        return RoutingDecision(Route.CLOUD, "cloud-first")

    def generate(self, request: AIRequest) -> AIResponse:
        self.decide(request)
        return self.cloud.generate(request)

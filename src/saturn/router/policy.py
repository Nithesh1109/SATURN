"""Hybrid AI routing policy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Provider(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


@dataclass(frozen=True)
class RoutingDecision:
    provider: Provider
    reason: str


class RouterPolicy:
    """Deterministic baseline policy; an LLM classifier can replace it later."""

    def choose(self, complexity: str) -> RoutingDecision:
        if complexity.lower() in {"complex", "reasoning", "unknown"}:
            return RoutingDecision(Provider.CLOUD, "complex task")
        return RoutingDecision(Provider.LOCAL, "fast/local task")

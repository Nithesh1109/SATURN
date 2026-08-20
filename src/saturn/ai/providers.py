"""Provider-neutral AI interface for SATURN."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderKind(str, Enum):
    """Supported provider families in SATURN's hybrid AI layer."""

    LOCAL = "local"
    CLOUD = "cloud"


@dataclass(frozen=True)
class AIRequest:
    """Common request contract accepted by all AI providers."""

    prompt: str
    system: str | None = None
    context: list[dict[str, str]] = field(default_factory=list)
    complexity: str = "simple"
    preferred_route: ProviderKind | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AIResponse:
    """Common provider response contract returned to the agent layer."""

    text: str
    provider: str
    model: str
    finish_reason: str = "stop"
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AIProviderConfig:
    """Configuration shared by local and cloud provider abstractions."""

    name: str
    kind: ProviderKind
    model: str
    enabled: bool = True
    endpoint: str | None = None
    timeout_seconds: float = 30.0
    api_key_env_var: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """Contract implemented by local and cloud AI providers."""

    name: str
    config: AIProviderConfig | None = None

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError

    def available(self) -> bool:
        return True

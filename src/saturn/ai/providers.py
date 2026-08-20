"""Provider-neutral AI interface for SATURN's cloud-first architecture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderKind(str, Enum):
    """Supported provider family for SATURN v1."""

    CLOUD = "cloud"


@dataclass(frozen=True)
class AIRequest:
    """Common request contract accepted by SATURN's cloud provider."""

    prompt: str
    system: str | None = None
    context: list[dict[str, str]] = field(default_factory=list)
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
    """Configuration for a cloud AI provider."""

    name: str
    kind: ProviderKind
    model: str
    enabled: bool = True
    endpoint: str | None = None
    timeout_seconds: float = 30.0
    api_key_env_var: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """Contract implemented by SATURN's AI provider."""

    name: str
    config: AIProviderConfig | None = None

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError

    def available(self) -> bool:
        return True

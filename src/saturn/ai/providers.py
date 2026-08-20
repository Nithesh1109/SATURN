"""Provider-neutral AI interface for SATURN."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AIRequest:
    prompt: str
    system: str | None = None
    context: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class AIResponse:
    text: str
    provider: str
    model: str
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """Contract implemented by local and cloud AI providers."""

    name: str

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError

    def available(self) -> bool:
        return True

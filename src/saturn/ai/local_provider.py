"""Local AI provider abstraction."""

from __future__ import annotations

from collections.abc import Callable

from .providers import AIProvider, AIProviderConfig, AIRequest, AIResponse, ProviderKind


class LocalAIProvider(AIProvider):
    """Adapter for local model backends (for example Ollama) via a stable contract."""

    def __init__(
        self,
        *,
        name: str = "local",
        model: str = "local-default",
        enabled: bool = True,
        endpoint: str | None = None,
        responder: Callable[[AIRequest], AIResponse] | None = None,
    ) -> None:
        self.name = name
        self.config = AIProviderConfig(
            name=name,
            kind=ProviderKind.LOCAL,
            model=model,
            enabled=enabled,
            endpoint=endpoint,
        )
        self._responder = responder

    def available(self) -> bool:
        assert self.config is not None
        return self.config.enabled

    def generate(self, request: AIRequest) -> AIResponse:
        if self._responder is not None:
            return self._responder(request)
        assert self.config is not None
        return AIResponse(
            text=request.prompt,
            provider=self.name,
            model=self.config.model,
            metadata={"kind": ProviderKind.LOCAL.value, "mode": "stub"},
        )

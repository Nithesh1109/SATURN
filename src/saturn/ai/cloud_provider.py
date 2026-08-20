"""Cloud AI provider abstraction."""

from __future__ import annotations

import os
from collections.abc import Callable

from .providers import AIProvider, AIProviderConfig, AIRequest, AIResponse, ProviderKind


class CloudAIProvider(AIProvider):
    """Adapter for cloud model APIs via the same provider contract as local models."""

    def __init__(
        self,
        *,
        name: str = "cloud",
        model: str = "cloud-default",
        enabled: bool = True,
        endpoint: str | None = None,
        api_key_env_var: str = "SATURN_CLOUD_API_KEY",
        require_api_key: bool = True,
        responder: Callable[[AIRequest], AIResponse] | None = None,
    ) -> None:
        self.name = name
        self.config = AIProviderConfig(
            name=name,
            kind=ProviderKind.CLOUD,
            model=model,
            enabled=enabled,
            endpoint=endpoint,
            api_key_env_var=api_key_env_var,
        )
        self._require_api_key = require_api_key
        self._responder = responder

    def available(self) -> bool:
        assert self.config is not None
        if not self.config.enabled:
            return False
        if not self._require_api_key:
            return True
        env_name = self.config.api_key_env_var
        return bool(env_name and os.getenv(env_name))

    def generate(self, request: AIRequest) -> AIResponse:
        if self._responder is not None:
            return self._responder(request)
        assert self.config is not None
        return AIResponse(
            text=request.prompt,
            provider=self.name,
            model=self.config.model,
            metadata={
                "kind": ProviderKind.CLOUD.value,
                "mode": "stub",
                "api_key_env_var": self.config.api_key_env_var,
            },
        )

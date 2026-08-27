"""NVIDIA NIM cloud AI provider for SATURN v1."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from urllib import error, request as urlrequest

from .providers import AIProvider, AIProviderConfig, AIRequest, AIResponse, ProviderKind


class CloudAIProvider(AIProvider):
    """OpenAI-compatible cloud adapter, configured for NVIDIA NIM by default."""

    DEFAULT_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
    # NVIDIA's current hosted endpoint exposes Nemotron 3.5 Lightning as a
    # free endpoint and positions it for agentic/tool-use workloads.
    DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
    DEFAULT_PLANNER_MAX_TOKENS = 384

    def __init__(
        self,
        *,
        name: str = "nvidia-nim",
        model: str | None = None,
        enabled: bool = True,
        endpoint: str | None = None,
        api_key_env_var: str = "NVIDIA_API_KEY",
        timeout_seconds: float = 60.0,
        responder: Callable[[AIRequest], AIResponse] | None = None,
    ) -> None:
        self.name = name
        self.config = AIProviderConfig(
            name=name,
            kind=ProviderKind.CLOUD,
            model=model or os.getenv("SATURN_CLOUD_MODEL", self.DEFAULT_MODEL),
            enabled=enabled,
            endpoint=endpoint or os.getenv("SATURN_CLOUD_ENDPOINT", self.DEFAULT_ENDPOINT),
            timeout_seconds=timeout_seconds,
            api_key_env_var=api_key_env_var,
        )
        self._responder = responder

    def available(self) -> bool:
        assert self.config is not None
        if not self.config.enabled:
            return False
        if self._responder is not None:
            return True
        env_name = self.config.api_key_env_var
        return bool(env_name and os.getenv(env_name))

    def generate(self, request: AIRequest) -> AIResponse:
        if self._responder is not None:
            return self._responder(request)

        assert self.config is not None
        if not self.available():
            raise RuntimeError(
                f"{self.name} is unavailable: set {self.config.api_key_env_var}"
            )

        messages: list[dict[str, str]] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.extend(request.context)
        messages.append({"role": "user", "content": request.prompt})

        payload: dict[str, object] = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.temperature is not None:
            payload["temperature"] = request.temperature

        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {os.environ[self.config.api_key_env_var]}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        http_request = urlrequest.Request(
            self.config.endpoint or self.DEFAULT_ENDPOINT,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urlrequest.urlopen(http_request, timeout=self.config.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Cloud AI request failed ({exc.code}): {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Cloud AI connection failed: {exc.reason}") from exc

        try:
            choice = raw["choices"][0]
            message = choice["message"]
            text = message["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Cloud AI returned an unexpected response") from exc

        metadata: dict[str, object] = {"kind": ProviderKind.CLOUD.value}
        user_text = text
        structured = self._parse_structured_response(text)
        if structured is not None:
            tool_calls = structured.get("tool_calls", structured.get("steps", []))
            if isinstance(tool_calls, list):
                metadata["tool_calls"] = tool_calls
            response_text = structured.get("response")
            if isinstance(response_text, str):
                user_text = response_text

        return AIResponse(
            text=user_text,
            provider=self.name,
            model=raw.get("model", self.config.model),
            finish_reason=choice.get("finish_reason", "stop"),
            metadata=metadata,
            raw=raw,
        )

    @staticmethod
    def _parse_structured_response(text: str) -> dict[str, object] | None:
        """Parse the planner JSON without making a second model/API call."""
        candidate = text.strip()
        if candidate.startswith("```"):
            lines = candidate.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            candidate = "\n".join(lines).strip()
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None

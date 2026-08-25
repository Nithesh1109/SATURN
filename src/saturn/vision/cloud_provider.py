"""Cloud vision adapter for SATURN's provider-independent perception layer."""

from __future__ import annotations

import json
import os
from urllib import error, request

from .perception import ScreenCapture, ScreenObservation


class CloudVisionProvider:
    """OpenAI-compatible vision adapter using the configured cloud endpoint."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        model: str | None = None,
        api_key_env_var: str = "NVIDIA_API_KEY",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.endpoint = endpoint or os.getenv(
            "SATURN_CLOUD_ENDPOINT", "https://integrate.api.nvidia.com/v1/chat/completions"
        )
        self.model = model or os.getenv("SATURN_VISION_MODEL", "")
        self.api_key_env_var = api_key_env_var
        self.timeout_seconds = timeout_seconds

    def available(self) -> bool:
        return bool(self.model and os.getenv(self.api_key_env_var))

    def analyze(self, capture: ScreenCapture) -> ScreenObservation:
        if not self.available():
            raise RuntimeError(
                f"Cloud vision is unavailable: set {self.api_key_env_var} and SATURN_VISION_MODEL"
            )

        prompt = (
            "Analyze this computer screenshot. Return JSON only with this schema: "
            '{"summary":"short description", "targets":[{"label":"target",'
            '"x":123,"y":456,"confidence":0.0}]} . '
            "Only report targets you can visually identify."
        )
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": capture.as_data_url()}},
        ]
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {os.environ[self.api_key_env_var]}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            req = request.Request(self.endpoint, data=body, headers=headers, method="POST")
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Cloud vision request failed ({exc.code}): {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Cloud vision connection failed: {exc.reason}") from exc

        try:
            text = raw["choices"][0]["message"]["content"]
            parsed = json.loads(text.strip().strip("`"))
            summary = str(parsed.get("summary", ""))
            targets = parsed.get("targets", [])
            if not isinstance(targets, list):
                targets = []
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Cloud vision returned an unexpected response") from exc

        return ScreenObservation(summary=summary, targets=tuple(targets))

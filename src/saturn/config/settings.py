"""SATURN configuration defaults."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "SATURN"
    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8765
    memory_path: str = "data/memory.json"
    local_ai_enabled: bool = True
    cloud_ai_enabled: bool = True

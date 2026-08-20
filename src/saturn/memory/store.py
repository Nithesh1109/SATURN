"""Local memory storage abstraction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LocalMemoryStore:
    """Simple JSON-backed memory store for SATURN."""

    def __init__(self, path: str | Path = "data/memory.json") -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def set(self, key: str, value: Any) -> None:
        data = self.load()
        data[key] = value
        self.save(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self.load().get(key, default)

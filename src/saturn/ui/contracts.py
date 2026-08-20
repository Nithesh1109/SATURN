"""Control Center communication contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UICommand:
    name: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class UIEvent:
    name: str
    payload: dict[str, Any]

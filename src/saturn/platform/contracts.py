"""Platform automation contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlatformAction:
    """A normalized laptop/platform action."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlatformResult:
    success: bool
    output: Any = None
    error: str | None = None

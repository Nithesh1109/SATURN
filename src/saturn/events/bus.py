"""Internal event bus contracts."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    """Small in-process pub/sub bus for SATURN components."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable[[dict[str, Any]], None]) -> None:
        self._handlers[event].append(handler)

    def publish(self, event: str, payload: dict[str, Any] | None = None) -> None:
        for handler in self._handlers[event]:
            handler(payload or {})

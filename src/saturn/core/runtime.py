"""SATURN core runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CoreStatus:
    state: str
    started_at: str


class SaturnCore:
    """Minimal long-running SATURN core runtime."""

    def __init__(self) -> None:
        self._started_at: str | None = None
        self._running = False

    def start(self) -> CoreStatus:
        if not self._running:
            self._started_at = datetime.now(timezone.utc).isoformat()
            self._running = True
        return self.status()

    def stop(self) -> CoreStatus:
        self._running = False
        return self.status()

    def status(self) -> CoreStatus:
        return CoreStatus(
            state="online" if self._running else "offline",
            started_at=self._started_at or "",
        )

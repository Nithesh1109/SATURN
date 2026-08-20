"""Local API contract for the SATURN core."""

from __future__ import annotations

from dataclasses import asdict

from .runtime import SaturnCore


class CoreAPI:
    """Application-facing interface to the SATURN core runtime."""

    def __init__(self, core: SaturnCore | None = None) -> None:
        self._core = core or SaturnCore()

    def health(self) -> dict[str, object]:
        """Return a serializable health/status payload."""
        return asdict(self._core.status())

    def start(self) -> dict[str, object]:
        """Start the core and return its status."""
        return asdict(self._core.start())

    def stop(self) -> dict[str, object]:
        """Stop the core and return its status."""
        return asdict(self._core.stop())

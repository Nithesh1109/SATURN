"""Conversation/task session state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentSession:
    """State carried through one SATURN interaction."""

    session_id: str
    history: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, role: str, content: Any) -> None:
        self.history.append({"role": role, "content": content})

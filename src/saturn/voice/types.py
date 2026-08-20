"""Voice pipeline contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioInput:
    data: bytes
    sample_rate: int
    channels: int = 1


@dataclass(frozen=True)
class Transcript:
    text: str
    confidence: float | None = None


@dataclass(frozen=True)
class SpeechOutput:
    text: str

from saturn.vision.perception import ScreenCapture, ScreenObservation
from saturn.vision.verification import VisualVerifier


class FakeVisionProvider:
    def __init__(self, observation: ScreenObservation) -> None:
        self.observation = observation

    def analyze(self, capture: ScreenCapture) -> ScreenObservation:
        return self.observation


def test_visual_verifier_accepts_confident_target() -> None:
    provider = FakeVisionProvider(
        ScreenObservation(
            summary="desktop",
            targets=({"label": "Chrome", "x": 100, "y": 200, "confidence": 0.95},),
        )
    )
    result = VisualVerifier(provider).verify_target_visible(
        ScreenCapture("screen.png", 800, 600), label="Chrome"
    )
    assert result.verified is True


def test_visual_verifier_rejects_low_confidence_target() -> None:
    provider = FakeVisionProvider(
        ScreenObservation(
            summary="desktop",
            targets=({"label": "Chrome", "x": 100, "y": 200, "confidence": 0.4},),
        )
    )
    result = VisualVerifier(provider).verify_target_visible(
        ScreenCapture("screen.png", 800, 600), label="Chrome"
    )
    assert result.verified is False


def test_visual_verifier_rejects_missing_target() -> None:
    provider = FakeVisionProvider(ScreenObservation(summary="desktop"))
    result = VisualVerifier(provider).verify_target_visible(
        ScreenCapture("screen.png", 800, 600), label="Chrome"
    )
    assert result.verified is False

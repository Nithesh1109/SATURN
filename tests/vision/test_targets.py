import pytest

from saturn.vision.targets import TargetValidator


def test_target_validator_accepts_target_inside_screen() -> None:
    target = TargetValidator().validate(
        {"label": "Chrome", "x": 742, "y": 421, "confidence": 0.94},
        width=1920,
        height=1080,
    )
    assert target.label == "Chrome"
    assert target.x == 742
    assert target.y == 421
    assert target.confidence == 0.94


@pytest.mark.parametrize(
    "target",
    [
        {"label": "", "x": 10, "y": 10, "confidence": 0.9},
        {"label": "Chrome", "x": -1, "y": 10, "confidence": 0.9},
        {"label": "Chrome", "x": 1920, "y": 10, "confidence": 0.9},
        {"label": "Chrome", "x": 10, "y": 1080, "confidence": 0.9},
        {"label": "Chrome", "x": 10, "y": 10, "confidence": 1.2},
    ],
)
def test_target_validator_rejects_unsafe_target(target) -> None:
    with pytest.raises(ValueError):
        TargetValidator().validate(target, width=1920, height=1080)


def test_target_validator_normalizes_multiple_targets() -> None:
    targets = TargetValidator().validate_many(
        (
            {"label": "Chrome", "x": 100, "y": 200, "confidence": 0.9},
            {"label": "Notepad", "x": 300, "y": 400, "confidence": 0.8},
        ),
        width=800,
        height=600,
    )
    assert [target.label for target in targets] == ["Chrome", "Notepad"]

from saturn.tools.validator import ActionValidator


def test_validator_accepts_valid_action() -> None:
    result = ActionValidator().validate("mouse_move", {"x": 100, "y": 200})
    assert result.allowed is True
    assert result.error is None


def test_validator_rejects_missing_arguments() -> None:
    result = ActionValidator().validate("mouse_move", {"x": 100})
    assert result.allowed is False
    assert "Missing required arguments" in result.error


def test_validator_rejects_invalid_coordinates() -> None:
    result = ActionValidator().validate("mouse_move", {"x": "bad", "y": 200})
    assert result.allowed is False
    assert "x must be an integer" in result.error


def test_validator_requires_confirmation_for_shutdown() -> None:
    result = ActionValidator().validate("shutdown_computer", {})
    assert result.allowed is False
    assert "confirmation=true" in result.error


def test_validator_allows_confirmed_shutdown() -> None:
    result = ActionValidator().validate("shutdown_computer", {"confirmation": True})
    assert result.allowed is True


def test_validator_rejects_empty_keyboard_text() -> None:
    result = ActionValidator().validate("keyboard_type", {"text": ""})
    assert result.allowed is False

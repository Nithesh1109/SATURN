from pathlib import Path

from saturn.vision.perception import ScreenCapture


def test_screen_capture_can_encode_png_as_data_url(tmp_path: Path) -> None:
    path = tmp_path / "screen.png"
    path.write_bytes(b"png-test-data")

    data_url = ScreenCapture(str(path), 100, 50).as_data_url()

    assert data_url.startswith("data:image/png;base64,")
    assert data_url.endswith("cG5nLXRlc3QtZGF0YQ==")

import os

import pytest

from saturn.vision.cloud_provider import CloudVisionProvider
from saturn.vision.perception import ScreenCapture


def test_cloud_vision_is_unavailable_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    provider = CloudVisionProvider(model="vision-test")
    assert provider.available() is False
    with pytest.raises(RuntimeError, match="NVIDIA_API_KEY"):
        provider.analyze(ScreenCapture(path="missing.png", width=1, height=1))


def test_cloud_vision_requires_a_model(monkeypatch) -> None:
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    provider = CloudVisionProvider(model="")
    assert provider.available() is False


def test_cloud_vision_parses_mocked_response(monkeypatch, tmp_path) -> None:
    from PIL import Image

    image = tmp_path / "screen.png"
    Image.new("RGB", (10, 10), "white").save(image)

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"model":"vision-test","choices":[{"message":{"content":"{\\"summary\\":\\"desktop\\",\\"targets\\":[{\\"label\\":\\"Chrome\\",\\"x\\":100,\\"y\\":200,\\"confidence\\":0.9}]}"}}]}'

    def fake_urlopen(req, timeout):
        assert req.get_header("Authorization") == "Bearer test-key"
        return FakeResponse()

    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    monkeypatch.setattr("saturn.vision.cloud_provider.request.urlopen", fake_urlopen)
    provider = CloudVisionProvider(model="vision-test")
    observation = provider.analyze(ScreenCapture(path=str(image), width=10, height=10))
    assert observation.summary == "desktop"
    assert observation.targets[0]["label"] == "Chrome"

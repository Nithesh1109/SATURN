import os

from saturn.ai.cloud_provider import CloudAIProvider
from saturn.ai.local_provider import LocalAIProvider
from saturn.ai.providers import AIRequest


def test_local_provider_available_when_enabled() -> None:
    provider = LocalAIProvider(enabled=True)

    assert provider.available() is True


def test_cloud_provider_requires_api_key_by_default() -> None:
    env_name = "SATURN_TEST_CLOUD_KEY"
    os.environ.pop(env_name, None)
    provider = CloudAIProvider(api_key_env_var=env_name)

    assert provider.available() is False


def test_cloud_provider_uses_env_key_when_present() -> None:
    env_name = "SATURN_TEST_CLOUD_KEY"
    os.environ[env_name] = "present-for-test"
    try:
        provider = CloudAIProvider(api_key_env_var=env_name)
        response = provider.generate(AIRequest("hello"))
        assert provider.available() is True
    finally:
        os.environ.pop(env_name, None)

    assert response.provider == "cloud"

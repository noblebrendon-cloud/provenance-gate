import pytest

from app.providers import DemoProvider, FireworksProvider, get_provider


def test_demo_provider_is_default(monkeypatch) -> None:
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.delenv("PROVIDER", raising=False)

    provider = get_provider()

    assert isinstance(provider, DemoProvider)


def test_demo_mode_overrides_fireworks_provider_without_key(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("PROVIDER", "fireworks")
    monkeypatch.delenv("FIREWORKS_API_KEY", raising=False)

    provider = get_provider()

    assert isinstance(provider, DemoProvider)


def test_fireworks_provider_requires_environment_key(monkeypatch) -> None:
    monkeypatch.delenv("FIREWORKS_API_KEY", raising=False)
    provider = FireworksProvider()

    with pytest.raises(RuntimeError, match="FIREWORKS_API_KEY"):
        provider.generate_claims("Synthetic source", "fixtures/demo.md")

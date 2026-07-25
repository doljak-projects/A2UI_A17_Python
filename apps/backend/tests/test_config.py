import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_loads_llm_config(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "sk-test-123")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "openai"
    assert settings.llm_api_key.get_secret_value() == "sk-test-123"
    assert settings.llm_model == "gpt-4o-mini"
    assert settings.llm_temperature == 0.7
    assert settings.llm_max_tokens == 1024


def test_settings_requires_api_key_and_model(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_rejects_invalid_provider(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test-123")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("LLM_PROVIDER", "invalid-provider")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)

import pytest

from src.services.ai import ai_client_factory
from src.services.ai.ai_client import AnthropicClient, FallbackAIClient, OpenAIClient


def test_raises_when_openai_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "y")

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        ai_client_factory.build_ai_client()


def test_raises_when_anthropic_key_missing(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        ai_client_factory.build_ai_client()


def test_builds_fallback_client_with_both_keys(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "y")

    client = ai_client_factory.build_ai_client()

    assert isinstance(client, FallbackAIClient)
    assert [type(c) for c in client._clients] == [OpenAIClient, AnthropicClient]

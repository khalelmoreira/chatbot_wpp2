import pytest
from src.types import AIClient, AIClientError, AIClientRetryableError
from src.services.ai.ai_client import FallbackAIClient


class _ScriptedClient(AIClient):
    """Client de teste que retorna um valor fixo ou levanta uma exceção configurada."""

    def __init__(self, result=None, error: Exception | None = None):
        self._result = result
        self._error = error
        self.calls = 0

    def extract_json(self, system_prompt: str, user_msg: str, schema: dict) -> dict:
        self.calls += 1
        if self._error:
            raise self._error
        return self._result

    def extract_text(self, system_prompt: str, user_msg: str) -> str:
        self.calls += 1
        if self._error:
            raise self._error
        return self._result


def test_primary_succeeds_fallback_never_called():
    primary = _ScriptedClient(result={"a": 1})
    fallback = _ScriptedClient(result={"a": 2})
    client = FallbackAIClient([primary, fallback])

    assert client.extract_json("sys", "msg", {}) == {"a": 1}
    assert fallback.calls == 0


def test_primary_retryable_error_falls_back():
    primary = _ScriptedClient(error=AIClientRetryableError("timeout"))
    fallback = _ScriptedClient(result={"a": 2})
    client = FallbackAIClient([primary, fallback])

    assert client.extract_json("sys", "msg", {}) == {"a": 2}
    assert primary.calls == 1
    assert fallback.calls == 1


def test_all_retryable_errors_reraise():
    primary = _ScriptedClient(error=AIClientRetryableError("timeout"))
    fallback = _ScriptedClient(error=AIClientRetryableError("rate limit"))
    client = FallbackAIClient([primary, fallback])

    with pytest.raises(AIClientRetryableError):
        client.extract_json("sys", "msg", {})


def test_non_retryable_error_propagates_immediately():
    primary = _ScriptedClient(error=AIClientError("chave invalida"))
    fallback = _ScriptedClient(result={"a": 2})
    client = FallbackAIClient([primary, fallback])

    with pytest.raises(AIClientError):
        client.extract_json("sys", "msg", {})
    assert fallback.calls == 0


def test_all_none_fields_is_not_a_failure():
    primary = _ScriptedClient(result={"razao_social": None, "cnpj": None})
    fallback = _ScriptedClient(result={"razao_social": "x", "cnpj": "y"})
    client = FallbackAIClient([primary, fallback])

    assert client.extract_json("sys", "msg", {}) == {"razao_social": None, "cnpj": None}
    assert fallback.calls == 0


def test_extract_text_falls_back_the_same_way():
    primary = _ScriptedClient(error=AIClientRetryableError("timeout"))
    fallback = _ScriptedClient(result="resposta ok")
    client = FallbackAIClient([primary, fallback])

    assert client.extract_text("sys", "msg") == "resposta ok"


def test_requires_at_least_one_client():
    with pytest.raises(ValueError):
        FallbackAIClient([])

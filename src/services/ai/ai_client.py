import json
import logging

import anthropic
import openai
from anthropic import Anthropic
from openai import OpenAI

from src.types import AIClient, AIClientError, AIClientRetryableError

logger = logging.getLogger(__name__)

# O histórico chega no vocabulário do domínio ("user" / "ai"); os SDKs falam
# "user" / "assistant". A tradução mora só aqui, na fronteira com o provedor.
_SDK_ROLE = {"user": "user", "ai": "assistant"}


def _with_history(
    history: list[dict[str, str]] | None, user_msg: str
) -> list[dict[str, str]]:
    turns = [
        {"role": _SDK_ROLE[m["role"]], "content": m["content"]}
        for m in (history or [])
        if m["role"] in _SDK_ROLE
    ]
    turns.append({"role": "user", "content": user_msg})
    return turns

def _map_openai_error(e: Exception) -> Exception:
    if isinstance(e, (openai.APITimeoutError, openai.APIConnectionError)):
        return AIClientRetryableError(f"Falha transitoria na OpenAI: {e}")
    if isinstance(e, openai.RateLimitError):
        return AIClientRetryableError(f"Rate limit da OpenAI: {e}")
    if isinstance(e, openai.APIStatusError):
        if e.status_code >= 500:
            return AIClientRetryableError(f"Erro no servidor da OpenAI ({e.status_code}): {e}")
        return AIClientError(f"Erro na chamada a OpenAI ({e.status_code}): {e}")
    return AIClientError(f"Erro inesperado ao chamar OpenAI: {e}")


class OpenAIClient(AIClient):
    """Provedor primario. Structured Outputs (response_format json_schema, strict) garante
    que o JSON retornado respeita `schema` — a validação de forma é feita pela API, não por
    instrução no prompt."""

    def __init__(self, api_key: str, model: str = "gpt-5-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def extract_json(
        self, system_prompt: str, user_msg: str, schema: dict,
        history: list[dict[str, str]] | None = None,
    ) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *_with_history(history, user_msg),
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "extraction",
                        "schema": schema,
                        "strict": True,
                    },
                },
            )
            message = response.choices[0].message
            if message.refusal:
                raise AIClientRetryableError(f"OpenAI recusou a extração: {message.refusal}")
            if not message.content:
                raise AIClientRetryableError("OpenAI retornou conteúdo vazio apesar do schema")
            return json.loads(message.content)
        except json.JSONDecodeError as e:
            raise AIClientRetryableError(f"OpenAI retornou JSON invalido apesar do schema: {e}") from e
        except AIClientError:
            raise
        except Exception as e:
            raise _map_openai_error(e) from e

    def extract_text(
        self, system_prompt: str, user_msg: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *_with_history(history, user_msg),
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise _map_openai_error(e) from e


def _map_anthropic_error(e: Exception) -> Exception:
    if isinstance(e, (anthropic.APITimeoutError, anthropic.APIConnectionError)):
        return AIClientRetryableError(f"Falha transitoria na Anthropic: {e}")
    if isinstance(e, (anthropic.RateLimitError, anthropic.OverloadedError)):
        return AIClientRetryableError(f"Rate limit/sobrecarga na Anthropic: {e}")
    if isinstance(e, anthropic.APIStatusError):
        if e.status_code >= 500:
            return AIClientRetryableError(f"Erro no servidor da Anthropic ({e.status_code}): {e}")
        return AIClientError(f"Erro na chamada a Anthropic ({e.status_code}): {e}")
    return AIClientError(f"Erro inesperado ao chamar Anthropic: {e}")


class AnthropicClient(AIClient):
    """Provedor de fallback. Structured Outputs via tool use forçado (strict) — mesmo
    contrato de determinismo do OpenAIClient, aplicado via `tool_choice` em vez de
    `response_format`."""

    TOOL_NAME = "extract"

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5", max_tokens: int = 2048):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def extract_json(
        self, system_prompt: str, user_msg: str, schema: dict,
        history: list[dict[str, str]] | None = None,
    ) -> dict:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=_with_history(history, user_msg),
                tools=[{
                    "name": self.TOOL_NAME,
                    "description": "Retorna os dados extraidos no formato especificado.",
                    "input_schema": schema,
                    "strict": True,
                }],
                tool_choice={"type": "tool", "name": self.TOOL_NAME},
            )
            for block in message.content:
                if block.type == "tool_use":
                    return block.input
            raise AIClientRetryableError("Anthropic não retornou um bloco tool_use apesar do tool_choice forçado")
        except AIClientError:
            raise
        except Exception as e:
            raise _map_anthropic_error(e) from e

    def extract_text(
        self, system_prompt: str, user_msg: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=_with_history(history, user_msg),
            )
            return "".join(block.text for block in message.content if block.type == "text")
        except Exception as e:
            raise _map_anthropic_error(e) from e


class FallbackAIClient(AIClient):
    """Tenta cada client em ordem; só avança para o proximo em AIClientRetryableError.
    Erros não-retentáveis (ex: chave invalida, request malformado) propagam imediatamente —
    são bugs estaticos, não ruido para contornar."""

    def __init__(self, clients: list[AIClient]):
        if not clients:
            raise ValueError("FallbackAIClient requer ao menos um client")
        self._clients = clients

    def extract_json(
        self, system_prompt: str, user_msg: str, schema: dict,
        history: list[dict[str, str]] | None = None,
    ) -> dict:
        last_error: Exception | None = None
        for client in self._clients:
            try:
                return client.extract_json(system_prompt, user_msg, schema, history)
            except AIClientRetryableError as e:
                logger.warning(f"{type(client).__name__} falhou, tentando proximo provedor: {e}")
                last_error = e
        raise AIClientRetryableError(f"Todos os provedores de IA falharam: {last_error}") from last_error

    def extract_text(
        self, system_prompt: str, user_msg: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        last_error: Exception | None = None
        for client in self._clients:
            try:
                return client.extract_text(system_prompt, user_msg, history)
            except AIClientRetryableError as e:
                logger.warning(f"{type(client).__name__} falhou, tentando proximo provedor: {e}")
                last_error = e
        raise AIClientRetryableError(f"Todos os provedores de IA falharam: {last_error}") from last_error

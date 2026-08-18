import os

from src.services.ai.ai_client import AnthropicClient, FallbackAIClient, OpenAIClient
from src.types import AIClient


def build_ai_client() -> AIClient:
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY não configurada")
    if not anthropic_key:
        raise RuntimeError("ANTHROPIC_API_KEY não configurada")
    return FallbackAIClient([
        OpenAIClient(api_key=openai_key, model="gpt-5-mini"),
        AnthropicClient(api_key=anthropic_key, model="claude-haiku-4-5"),
    ])

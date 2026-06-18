from src.models.prompts.nfse_prompts import PROMPT_EXTRACT_NFSE_GEMMA

from src.models.prompts.conversation_prompts import (
    PROMPT_HAS_INTENT,
    PROMPT_NO_INTENT_RESPONSE,
)

__all__ = [
    "PROMPT_EXTRACT_NFSE_GEMMA",
    "PROMPT_EXTRACT_NFSE_CLAUDE",
    "TOOL_EXTRACT_NFSE",
    "PROMPT_PRESTADOR_CADASTRO",
    "PROMPT_ENDERECO_GEMMA",
]
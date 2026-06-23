# DATACLASSES
from src.types.context import (
    ContextBase,
    ContextPrestador,
    ContextTomador,
    DadosPrestador,
    DadosTomador,
    ProjectPrestador,
    Tomador,
    Servico,
    ResultadoOnboarding,
    Valores,
    ResultadoValidacao,
    Endereco,
)

# Enums (tipos de estado)
from src.types.user import User, EstadoUser
from src.types.conversation import (
    IncomingMessage,
    AIResponse,
    AIClient,
    BotaoResponse,
)

# De models (enums de estado que deveriam estar em types)
from src.types.conversation_state import ConversationStatus

from src.types.nfse import NfNotFoundError, EventsNotaas, StatusInvoice, NfseStatus, PayloadNotaas

__all__ = [
    # Contexts
    "ContextBase",
    "DadosPrestador",
    "DadosTomador",
    "Tomador",
    "Servico",
    "Valores",
    "ResultadoValidacao",
    "Endereco",
    "ProjectPrestador",
    "ResultadoOnboarding",
    # User
    "User",
    "EstadoUser",
    # Conversation
    "IncomingMessage",
    "AIResponse",
    "AIClient",
    "BotaoResponse",
    "ConversationStatus",
    "NfseStatus",
    "EventsNotaas",
    "PayloadNotaas",
    "StatusInvoice"
    "NfNotFoundError",
]
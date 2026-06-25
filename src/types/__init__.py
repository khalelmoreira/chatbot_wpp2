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
from src.types.wpp_msg import (
    IncomingMessage,
    AIResponse,
    AIClient,
    BotaoResponse,
    MessageType,
    Role,
)

from src.types.conversation import ConversationStatus, StatusResumo, IntentTipo
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
    "StatusResumo",
    "BotaoResponse",
    "ConversationStatus",
    "NfseStatus",
    "EventsNotaas",
    "PayloadNotaas",
    "StatusInvoice"
    "NfNotFoundError",
    "IntentTipo",
    "Role",
    "MessageType",
]
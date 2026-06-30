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
    MsgConvType,
    Role,
    TypeMessage,
    BotaoId,
)

from src.types.conversation import (
    ConversationStatus,
    StatusResumo,
    IntentTipo,
    HistoryResumo,
)
from src.types.nfse import (
    NfNotFoundError,
    EventsNotaas,
    StatusInvoice,
    NfseStatus,
    PayloadNotaas,
)

__all__ = [
    # Contexts
    "ContextBase",
    "DadosPrestador",
    "DadosTomador",
    "ContextTomador",
    "ContextPrestador",
    "Tomador",
    "Servico",
    "Valores",
    "ResultadoValidacao",
    "Endereco",
    "ProjectPrestador",
    "ResultadoOnboarding",
    "NfNotFoundError",
    "StatusInvoice",
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
    "MsgConvType",
    "TypeMessage",
    "BotaoId",
    "HistoryResumo",
]
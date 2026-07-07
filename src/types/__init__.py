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
from src.types.user import User, UserStatus
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
    MsgResumo,
)
from src.types.nfse import (
    EventsNotaas,
    StatusInvoice,
    NfseStatus,
    PayloadNotaas,
)

from src.types.exceptions import (
    NfNotFoundError,
    InvalidTransactionError,
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
    "UserStatus",
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
    "MsgResumo",
    "InvalidTransactionError",
]
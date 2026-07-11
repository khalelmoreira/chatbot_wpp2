# DATACLASSES
from src.types.context import (
    ContextBase,
    ContextPrestador,
    ContextTomador,
    PrestadorData,
    TomadorData,
    ProjectPrestador,
    Tomador,
    Servico,
    ResultadoOnboarding,
    Valores,
    ValidationResult,
    Address,
)

# Enums (tipos de estado)
from src.types.user import (
    User,
    UserStatus,
    IntentUserType,
)
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
    IntentType,
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
    NtaasCertificadoError,
    NtassOrgError,
    CnpjJaCadastradoError,
    LimitePlanoAtingidoError,
    DadosInvalidosError,
)

__all__ = [
    # Contexts
    "ContextBase",
    "PrestadorData",
    "TomadorData",
    "ContextTomador",
    "ContextPrestador",
    "Tomador",
    "Servico",
    "Valores",
    "ValidationResult",
    "Address",
    "ProjectPrestador",
    "ResultadoOnboarding",
    "NfNotFoundError",
    "StatusInvoice",
    # User
    "User",
    "UserStatus",
    "IntentUserType",
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
    "IntentType",
    "Role",
    "MsgConvType",
    "TypeMessage",
    "BotaoId",
    "HistoryResumo",
    "MsgResumo",
    "InvalidTransactionError",
    "NtaasCertificadoError",
    "NtassOrgError",
    "CnpjJaCadastradoError",
    "LimitePlanoAtingidoError",
    "DadosInvalidosError",
]
# DATACLASSES
from chatbot_wpp2.src.types.base import (
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
    ConvStatus,
    AIClient,
    BotaoResponse,
    MsgConvType,
    Role,
    MsgType,
    BotaoId,
)

from src.types.conversation import (
    ConvStatus,
    StatusResumo,
    IntentType,
    HistoryResumo,
    MsgResumo,
)
from chatbot_wpp2.src.types.nfs import (
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
    "ConvStatus",
    "AIClient",
    "StatusResumo",
    "BotaoResponse",
    "ConvStatus",
    "NfseStatus",
    "EventsNotaas",
    "PayloadNotaas",
    "StatusInvoice"
    "NfNotFoundError",
    "IntentType",
    "Role",
    "MsgConvType",
    "MsgType",
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
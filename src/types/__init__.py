# DATACLASSES
from src.types.base import (
    ContextBase,
    UserStatus,
    User,
    ValidationResult,
    Address,
)

# Enums (tipos de estado)
from src.types.user import (
    IntentUserType,
    Prestador,
    PrestadorData,
    ContextPrestador,
)

from src.types.tomador import (
    DocTomadorType,
    Doc,
    TomadorT,
    Tomador,
    Servico,
    Valores,
    TomadorData,
    ContextTomador,
)

from src.types.wpp_msg import (
    IncomingMessage,
    BotaoResponse,
    MsgConvType,
    Role,
    MsgType,
    BotaoId,
    Message,
)

from src.types.conversation import (
    ConvStatus,
    IntentType,
    StatusResumo,
    HistoryResumo,
    MsgResumo,
    Conversation,
)
from src.types.nfs import (
    NfseStatus,
    EventsNotaas,
    StatusInvoice,
    PayloadNotaas,
    Nfs,
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
    # Base
    "ContextBase",
    "UserStatus",
    "User",
    "ValidationResult",
    "Address",
    # User
    "IntentUserType",
    "Prestador",
    "PrestadorData",
    "ContextPrestador",
    # tomador
    "DocTomadorType",
    "Doc",
    "TomadorT",
    "Tomador",
    "Servico",
    "Valores",
    "TomadorData",
    "ContextTomador",
    # wpp_msg
    "Message",
    "IncomingMessage",
    "BotaoResponse",
    "MsgConvType",
    "Role",
    "MsgType",
    "BotaoId",
    # Conversation
    "ConvStatus",
    "IntentType",
    "StatusResumo",
    "HistoryResumo",
    "MsgResumo",
    "Conversation",
    # nfs
    "NfseStatus",
    "EventsNotaas",
    "StatusInvoice",
    "PayloadNotaas",
    "Nfs",
    # exceptions
    "NfNotFoundError",
    "InvalidTransactionError",
    "NtaasCertificadoError",
    "NtassOrgError",
    "CnpjJaCadastradoError",
    "LimitePlanoAtingidoError",
    "DadosInvalidosError",
]
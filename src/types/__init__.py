from src.types.base import (
    ContextBase,
    ValidationResult,
    FromDictable,
    Mergeable,
    IsDataclass,
)

from src.types.user import (
    UserStatus,
    User,
    Address,
    IntentUserType,
    Prestador,
    PrestadorData,
)

from src.types.tomador import (
    DocTomadorType,
    Doc,
    TomadorT,
    Tomador,
    Servico,
    Valores,
    TomadorData,
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
    Conversation,
)
from src.types.nfs import (
    NfseStatus,
    EventsNotaas,
    StatusInvoice,
    PayloadNotaas,
    Nfs,
    NfsJob,
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

from src.types.handler_result import (
    HandlerResult,
)

from src.types.resumo_types import (
    StatusResumo,
    HistoryResumo,
    MsgResumo,
)

from src.types.ai_types import (
    AIClient,
    AIPrompt,
    AIExtractor,
    ExtractionConfig,
    ClassificationConfig,
    AIInterpreter,
    ResponseConfig,
    PrestRespKey,
    PrestClassKey,
    PrestExtractKey,
    TomRespKey,
    TomClassKey,
    TomExtractKey,
)

from src.types.context import (
    ContextPrestador,
    ContextTomador,
)

from src.types.mixins import (
    MergeableMixin,
    TextMixin,
    FromDictMixin,
)

__all__ = [
    # Base
    "ContextBase",
    "Mergeable",
    "IsDataclass",
    "ValidationResult",
    "User",
    "FromDictable",
    # User
    "UserStatus",
    "Address",
    "IntentUserType",
    "Prestador",
    "PrestadorData",
    # tomador
    "DocTomadorType",
    "Doc",
    "TomadorT",
    "Tomador",
    "Servico",
    "Valores",
    "TomadorData",
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
    "Conversation",
    # nfs
    "NfseStatus",
    "EventsNotaas",
    "StatusInvoice",
    "PayloadNotaas",
    "Nfs",
    "NfsJob",
    # exceptions
    "NfNotFoundError",
    "InvalidTransactionError",
    "NtaasCertificadoError",
    "NtassOrgError",
    "CnpjJaCadastradoError",
    "LimitePlanoAtingidoError",
    "DadosInvalidosError",
    # handler result
    "HandlerResult",
    # resumo_types
    "StatusResumo",
    "HistoryResumo",
    "MsgResumo",
    # ai_types
    "AIClient",
    "AIPrompt",
    "AIExtractor",
    "ExtractionConfig",
    "ClassificationConfig",
    "AIInterpreter",
    "ResponseConfig",
    "PrestRespKey",
    "PrestClassKey",
    "PrestExtractKey",
    "TomRespKey",
    "TomClassKey",
    "TomExtractKey",
    # context
    "ContextPrestador",
    "ContextTomador",
    # mixins
    "MergeableMixin",
    "TextMixin",
    "FromDictMixin",
]
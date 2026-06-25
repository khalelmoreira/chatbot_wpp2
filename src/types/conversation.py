from enum import Enum
from dataclasses import dataclass

class ConversationStatus(str, Enum):
    COLLECTING  = "COLLECTING"
    CONFIRMING  = "CONFIRMING"
    QUEUED      = "QUEUED"
    DONE        = "DONE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

class IntentTipo(str, Enum):
    EMITIR   = "EMITIR"
    CONSULTA = "CONSULTA"
    NENHUM   = "NENHUM"

@dataclass
class ResultExtract:
    campos: dict
    parece_pergunta: bool

@dataclass
class StatusResumo:
    nf_status: str | None = None
    erro_msg: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    invoice_id: str | None = None
    draft: str | None = None
    requested_at: str | None = None
    cancelled_at: str | None = None
    emitido_em: str | None = None
from enum import StrEnum
from dataclasses import dataclass

class ConvStatus(StrEnum):
    COLLECTING  = "COLLECTING"
    CONFIRMING  = "CONFIRMING"
    QUEUED      = "QUEUED"
    DONE        = "DONE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

class IntentType(StrEnum):
    EMITIR   = "EMITIR"
    CONSULTA = "CONSULTA"
    NENHUM   = "NENHUM"

@dataclass
class ResultExtract:
    campos: dict
    parece_pergunta: bool

@dataclass
class StatusResumo:
    nf_status:    str | None = None
    erro_msg:     str | None = None
    created_at:   str | None = None
    updated_at:   str | None = None
    invoice_id:   str | None = None
    draft:        str | None = None
    requested_at: str | None = None
    cancelled_at: str | None = None
    emitido_em:   str | None = None

@dataclass
class HistoryResumo:
    id:                int | None = None
    status:            str | None = None
    conversation_id:   int | None = None
    tentativas:        int | None = None
    nome:              str | None = None
    cnpj:              str | None = None
    descricao_servico: str | None = None
    valor_total:       str | None = None
    requested_at:      str | None = None
    created_at:        str | None = None
    invoice_id:        str | None = None
    emitido_em:        str | None = None
    issued_at:         str | None = None
    erro_code:         str | None = None
    erro_msg:          str | None = None
    cancelled_at:      str | None = None

@dataclass
class MsgResumo:
    role:    str | None = None
    content: str | None = None
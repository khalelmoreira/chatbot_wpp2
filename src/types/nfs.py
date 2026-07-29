from enum import StrEnum
from dataclasses import dataclass, fields

from src.types.base import Address

class NfseStatus(StrEnum):
    QUEUED      = "QUEUED"
    PROCESSING  = "PROCESSING"
    ISSUED      = "ISSUED"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"


class EventsNotaas(StrEnum):
    NFSE_ISSUED     = "nfse.issued"
    NFSE_ERROR      = "nfse.error"
    NFSE_CANCELLED  = "nfse.cancelled"
    NFSE_DOCS_READY = "nfse.documents_ready"
    WEBHOOK_TEST    = "webhook.test"

@dataclass(frozen=True)
class StatusInvoice:
    status:        str
    ch_nfse:       str | None = None
    ch_nfse:       str | None = None
    n_nfse:        str | None = None
    issued_at:     str | None = None
    error_code:    str | None = None
    error_message: str | None = None

@dataclass
class PayloadNotaas:
    event: str | None
    data:  dict[str, str] | None

@dataclass
class Nfs:
    id:                        int
            
    prestador_id:              int
    tomador_id:                int
    conv_id:           int

    nome:                      str
    cnpj:                      str
            
    descricao_servico:         str
        
    valor_total:               float
    aliquota_iss:              float = 5.0

    idempotency_key:           str | None = None
    status:                    NfseStatus | None = None
    tentativas:                int | None = 0
    payload_enviado:           str | None = None
    requested_at:              str | None = None
    created_at:                str | None = None
    updated_at:                str | None = None

    phone:                     str | None = None
    invoice_id:                str | None = None
    cpf:                       str | None = None
    email:                     str | None = None
            
    cep:                       str | None = None
    address:                   Address | None = None
            
    codigo_servico:            str | None = None
    iss_retido:                bool | None = False
    competencia:               str | None = None
    referencia:                str | None = None
            
    ch_nfse:                   str | None = None
    n_nfse:                    str | None = None
    issued_at:                 str | None = None
    ambiente:                  str | None = None
    pdf_url:                   str | None = None
    xml_url:                   str | None = None
    documents_cached:          bool | None = False
    document_status:           str | None = None
    emitido_em:                str | None = None
            
    erro_code:                 str | None = None
    erro_msg:                  str | None = None
    erro_json:                 str | None = None
            
    processado_em:             str | None = None
    cancelled_at:              str | None = None
    cancel_xml_url:            str | None = None

@dataclass
class NfsJob:
    id:                int
    conv_id:           int
    nome:              str
    cnpj:              str
    descricao_servico: str
    valor_total:       float
    aliquota_iss:      float
    tentativas:        int

    @classmethod
    def from_dict(cls, d: dict) -> "NfsJob":
        campos = {f.name for f in fields(cls)}
        faltantes = campos - d.keys()
        if faltantes:
            raise ValueError(f"campos faltantes: {faltantes}")
        return cls(**{k: d[k] for k in campos})
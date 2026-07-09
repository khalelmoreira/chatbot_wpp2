from enum import StrEnum
from dataclasses import dataclass

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
    status: str
    ch_nfse: str | None       = None
    ch_nfse: str | None       = None
    n_nfse: str | None        = None
    issued_at: str | None     = None
    error_code: str | None    = None
    error_message: str | None = None

@dataclass
class PayloadNotaas:
    event: str | None
    data: dict[str, str] | None
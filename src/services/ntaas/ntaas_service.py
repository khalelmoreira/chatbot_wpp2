import logging

from src.services.ntaas.nfse_service import NfseService
from src.types import EventsNotaas, PayloadNotaas

logger = logging.getLogger(__name__)

class NtaasWebhook:
    def __init__(self, payload: dict):
        self.payload = payload
        
    def parse(self) -> PayloadNotaas:

        event_raw = self.payload.get("event")
        if not event_raw:
            raise ValueError("evento nao informado")

        try:
            event = EventsNotaas(event_raw)

        except ValueError as e:
            raise ValueError(f"evento desconhecido: {event_raw}") from e

        data = self.payload.get("data")
        return PayloadNotaas(event=event, data=data)
        
    def dispatch(self, payload: PayloadNotaas):
        if payload.event == EventsNotaas.WEBHOOK_TEST:
            logger.debug("webhook notaas: WEBHOOK_TEST recebido")
            return None

        service = NfseService(payload.data)

        match payload.event:
            case EventsNotaas.NFSE_ISSUED:
                return service.issued()

            case EventsNotaas.NFSE_ERROR:
                return service.error()

            case EventsNotaas.NFSE_CANCELLED:
                return service.cancelled()

            case EventsNotaas.NFSE_DOCS_READY:
                return service.docs_ready()
from src.services.notaas.nfse_service import NfseService
from src.types import NfNotFoundError, EventsNotaas, PayloadNotaas

class NotaasWebhook:
    def __init__(self, payload_raw):
        self.payload_raw = payload_raw

    def processar_webhook_notaas(self):

        payload = self._parse()
        return self._dispatch(payload=payload)
        
    def _parse(self) -> PayloadNotaas | dict:

        try:
            event = self.payload_raw.get("event")
            print(f"EVENTO: {event}\n")

            if not event:
                return {
                    "success": False,
                    "error": "evento não informado"
                }

            data = self.payload_raw.get("data")
            print(f"DATA: {data}\n")

            return PayloadNotaas(event=event, data=data)

        except NfNotFoundError as e:
            print(f"\n[ERRO WEBHOOK] {str(e)}")

            return {
                "success": False,
                "error": str(e)
            }
        
    def _dispatch(self, payload: PayloadNotaas):

        events = EventsNotaas(payload.event)
        service = NfseService(payload.data)

        match events:
            case EventsNotaas.NFSE_ISSUED:
                return service.issued()
            
            case EventsNotaas.NFSE_ERROR:
                return service.error()
            
            case EventsNotaas.NFSE_CANCELLED:
                return service.cancelled()
            
            case EventsNotaas.NFSE_DOCS_READY:
                return service.docs_ready()
            
            case EventsNotaas.WEBHOOK_TEST:
                return "OK", 200
import json
from src.services.notaas.nfse_service import NfseService
from src.types import NfNotFoundError

def notaas_webhook(payload: dict):

    try:
        print("\n========== WEBHOOK RECEBIDO ==========")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        #EVENTO PRINCIPAL

        evento = payload.get("event")
        print(f"EVENTO: {evento}\n")

        data = payload.get("data")
        print(f"DATA: {data}\n")

        if not evento:
            return {
                "success": False,
                "error": "evento não informado"
            }
        
        print(f"\n[INFO] Evento recebido: {evento}")

        service = NfseService(data)

        #roteamento de eventos

        if evento == "nfse.issued":
            return service.issued()
        
        elif evento == "nfse.error":
            return service.error()
        
        elif evento == "nfse.cancelled":
            return service.cancelled()
        
        elif evento == "nfse.documents_ready":
            return service.docs_ready()
        
        elif evento == "webhook.test":
            return 200
        
        else:
            print("evento não conhecido")
            return {
                "success": True,
                "mensagem": "evento ignorado"
            }
        
    except NfNotFoundError as e:
        print(f"\n[ERRO WEBHOOK] {str(e)}")

        return {
            "success": False,
            "error": str(e)
        }
from flask import Flask, request, jsonify
import hashlib
import hmac
import os
from datetime import datetime
import json

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRETS_NOTAAS")


def verificar_assinatura(payload, assinatura):

    assinatura_esperada = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        assinatura_esperada,
        assinatura
    )



def processar_webhook_notaas(payload: dict):
    try:

        print("\n========== WEBHOOK RECEBIDO ==========")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        #EVENTO PRINCIPAL

        evento = payload.get("event")
        data = payload.get("data")

        if not evento:
            return {
                "success": False,
                "error": "evento não informado"
            }
        
        print(f"\n[INFO] Evento recebido: {evento}")

        #roteamento de eventos

        if evento == "nfse.issued":
            return nfse_issued(data)
        
        elif evento == "nfse.error":
            return nfse_error(data)
        
        elif evento == "nfse.cancelled":
            return nfse_cancelled(data)
        
        elif evento == "nfse.documents_ready":
            return nfse_docs_ready(data)
        
        else:
            print("evento não conhecido")
            return {
                "success": True,
                "mensagem": "evento ignorado"
            }
        
    except Exception as e:
        print(f"\n[ERRO WEBHOOK] {str(e)}")

        return {
            "success": False,
            "error": str(e)
        }
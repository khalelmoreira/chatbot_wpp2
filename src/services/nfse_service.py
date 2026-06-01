import requests
import os
import hashlib
import hmac

API_KEY = os.getenv("NOTAAS_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET_NOTAAS")

def verificar_ass(payload, assinatura):
    assinatura_esperada = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        assinatura_esperada,
        assinatura
    )


def emitir_nf(dados):
    url = "https://platform.notaas.com.br/api/v1/emitir"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    response = requests.post(url, json=dados, headers=headers)

    if response.status_code not in [200, 201, 202]:
        raise Exception(f"Erro na emissão: {response.text}")
    
    return response.json()

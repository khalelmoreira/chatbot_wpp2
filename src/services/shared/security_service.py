import os
import hashlib
import hmac

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
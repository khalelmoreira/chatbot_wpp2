import hmac
import os
import hashlib

def validar_assinatura(request):

    assinatura_recebida = request.headers.get("X-Hub-Signature-256")

    if not assinatura_recebida:
        return False
    
    assinatura_recebida = assinatura_recebida.split("=")[1]

    body = request.get_data()

    hash_gerado = hmac.new(
        os.getenv("APP_SECRET").encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(hash_gerado, assinatura_recebida)
import os
import hashlib
import hmac

def verificar_ass(payload_raw: bytes, assinatura_arrived: str) -> bool:
    
    secret = os.environ["WEBHOOK_SECRET_NOTAAS"].encode()
    expected = "sha256=" + hmac.new(
        secret, payload_raw, hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(assinatura_arrived, expected)
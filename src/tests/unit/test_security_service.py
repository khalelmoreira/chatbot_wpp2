import hashlib
import hmac

from src.services.validators.security_service import validate_signature


def _assinar(payload: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def test_validate_signature_aceita_assinatura_correta(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET_NOTAAS", "segredo-123")
    payload = b'{"event": "nfse.issued"}'

    assert validate_signature(payload, _assinar(payload, "segredo-123")) is True


def test_validate_signature_rejeita_assinatura_de_outro_segredo(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET_NOTAAS", "segredo-123")
    payload = b'{"event": "nfse.issued"}'

    assert validate_signature(payload, _assinar(payload, "outro-segredo")) is False


def test_validate_signature_rejeita_payload_adulterado(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET_NOTAAS", "segredo-123")
    assinatura = _assinar(b'{"event": "nfse.issued"}', "segredo-123")

    assert validate_signature(b'{"event": "nfse.cancelled"}', assinatura) is False


def test_validate_signature_rejeita_assinatura_malformada(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET_NOTAAS", "segredo-123")
    payload = b'{"event": "nfse.issued"}'

    assert validate_signature(payload, "nao-comeca-com-sha256=") is False

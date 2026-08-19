from src.services.ntaas.webhook_validator_service import WebhookValidatorService


def test_validar_recusa_sem_assinatura():
    ok, error = WebhookValidatorService().validar(b"{}", None)
    assert ok is False
    assert error == "assinatura ausente"


def test_validar_recusa_assinatura_invalida(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET_NOTAAS", "segredo-123")
    ok, error = WebhookValidatorService().validar(b"{}", "sha256=nao-bate")
    assert ok is False
    assert error == "assinatura invalida"


def test_validar_aceita_assinatura_correta(monkeypatch):
    import hashlib
    import hmac

    monkeypatch.setenv("WEBHOOK_SECRET_NOTAAS", "segredo-123")
    payload = b'{"event": "nfse.issued"}'
    assinatura = "sha256=" + hmac.new(b"segredo-123", payload, hashlib.sha256).hexdigest()

    ok, error = WebhookValidatorService().validar(payload, assinatura)
    assert ok is True
    assert error is None

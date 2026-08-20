from pathlib import Path

import pytest
from flask import Flask

from src.routes import ntaas as ntaas_module
from src.routes import wpp as wpp_module
from src.routes.ntaas import ntaas_bp
from src.routes.wpp import wpp_bp
from src.types import HandlerResult

MODELS_DIR = str(Path(__file__).resolve().parents[3] / "models")


@pytest.fixture
def client():
    # Mirrors app.py's create_app(): templates (token_invalido.html, upload_form.html)
    # actually live in src/models/, not a "templates/" dir next to app.py.
    app = Flask("test_app", template_folder=MODELS_DIR)
    app.register_blueprint(wpp_bp)
    app.register_blueprint(ntaas_bp)
    app.testing = True
    return app.test_client()


def test_wpp_webhook_get_accepts_matching_verify_token(client, monkeypatch):
    monkeypatch.setenv("VERIFY_TOKEN", "meu-token")

    resp = client.get("/webhook", query_string={"hub.verify_token": "meu-token", "hub.challenge": "12345"})

    assert resp.status_code == 200
    assert resp.data == b"12345"


def test_wpp_webhook_get_rejects_wrong_verify_token(client, monkeypatch):
    monkeypatch.setenv("VERIFY_TOKEN", "meu-token")

    resp = client.get("/webhook", query_string={"hub.verify_token": "errado", "hub.challenge": "12345"})

    assert resp.status_code == 403


def test_wpp_webhook_post_ignores_empty_body(client, monkeypatch):
    calls = []
    monkeypatch.setattr(wpp_module, "wpp_handler", lambda data: calls.append(data))

    resp = client.post("/webhook", json={})

    assert resp.status_code == 200
    assert calls == []


def test_wpp_webhook_post_delegates_to_handler(client, monkeypatch):
    calls = []
    monkeypatch.setattr(wpp_module, "wpp_handler", lambda data: calls.append(data))

    payload = {"entry": [{"id": "123"}]}
    resp = client.post("/webhook", json=payload)

    assert resp.status_code == 200
    assert calls == [payload]


def test_ntaas_webhook_delegates_and_reflects_handler_result(client, monkeypatch):
    monkeypatch.setattr(
        ntaas_module, "ntaas_handler",
        lambda payload_raw, signature, delivery_id: HandlerResult(
            401, {"success": False, "error": "assinatura invalida"},
        ),
    )

    resp = client.post("/webhook/notaas", data=b"{}", headers={"X-Notaas-Signature": "bad"})

    assert resp.status_code == 401
    assert resp.get_json() == {"success": False, "error": "assinatura invalida"}


def test_ntaas_webhook_passes_headers_and_body_through(client, monkeypatch):
    captured = {}

    def fake_handler(payload_raw, signature, delivery_id):
        captured.update(payload_raw=payload_raw, signature=signature, delivery_id=delivery_id)
        return HandlerResult(200, {"success": True})

    monkeypatch.setattr(ntaas_module, "ntaas_handler", fake_handler)

    resp = client.post(
        "/webhook/notaas", data=b'{"event": "nfse.issued"}',
        headers={"X-Notaas-Signature": "sha256=abc", "X-Notaas-Delivery": "delivery-1"},
    )

    assert resp.status_code == 200
    assert captured == {
        "payload_raw": b'{"event": "nfse.issued"}',
        "signature": "sha256=abc",
        "delivery_id": "delivery-1",
    }


def test_process_upload_delegates_to_handler(client, monkeypatch):
    monkeypatch.setattr(
        ntaas_module, "certificate_upload_handler",
        lambda token, arq, pasw: HandlerResult(200, {"success": True}),
    )

    resp = client.post("/upload-certificate/tok123", data={"pasw": "1234"})

    assert resp.status_code == 200
    assert resp.get_json() == {"success": True}


def test_form_upload_renders_template_for_invalid_token(client, monkeypatch):
    monkeypatch.setattr(
        ntaas_module, "certificate_form_handler",
        lambda token: HandlerResult(410, {"success": False}),
    )

    resp = client.get("/upload-certificate/tok123")

    assert resp.status_code == 410

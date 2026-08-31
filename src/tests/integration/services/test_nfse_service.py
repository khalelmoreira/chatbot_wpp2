import json

import pytest

from src.services.ntaas.nfse_service import NfseService
from src.services.ntaas.ntaas_service import NtaasWebhook
from src.types import EventsNotaas


def _setup_nf(db, invoice_id: str = "inv-123") -> dict:
    phone = "5511988887777"
    prestador_id = db.insert("prestador", data={"phone": phone, "status": "ACTIVE"}, returning="id")
    tomador_id = db.insert(
        "tomador",
        data={"prestador_id": prestador_id, "name": "Cliente", "cnpj": "11222333000181"},
        returning="id",
    )
    conv_id = db.insert(
        "conversations",
        data={"prestador_id": prestador_id, "phone": phone, "status": "QUEUED", "draft_json": "{}"},
        returning="id",
    )
    nf_id = db.insert(
        "nfs",
        data={
            "prestador_id": prestador_id,
            "tomador_id": tomador_id,
            "conv_id": conv_id,
            "idempotency_key": "key-1",
            "payload_enviado": "{}",
            "nome": "Cliente",
            "cnpj": "11222333000181",
            "descricao_servico": "Consultoria",
            "valor_total": 1500,
            "invoice_id": invoice_id,
        },
        returning="id",
    )
    return {"prestador_id": prestador_id, "conv_id": conv_id, "nf_id": nf_id, "phone": phone}


def test_issued_marks_nf_done_and_resets_conversation(db):
    ids = _setup_nf(db)

    NfseService({"invoiceId": "inv-123", "chNFSe": "CH-1", "numeroNfe": "1"}).issued()

    nf = db.select_one("nfs", where={"id": ids["nf_id"]})
    assert nf["status"] == "DONE"
    assert nf["ch_nfse"] == "CH-1"
    assert nf["n_nfse"] == "1"

    conv = db.select_one("conversations", where={"id": ids["conv_id"]})
    assert conv["status"] == "COLLECTING"
    assert json.loads(conv["draft_json"]) == {}

    msgs = db.select("messages", where={"prestador_id": ids["prestador_id"]})
    assert any(m["role"] == "AI" and "emitida com sucesso" in m["content"] for m in msgs)


def test_error_marks_nf_error_with_message(db):
    ids = _setup_nf(db)

    NfseService({
        "invoiceId": "inv-123",
        "errorMessage": "CNPJ invalido",
        "errors": [{"Codigo": "E1", "Descricao": "CNPJ invalido"}],
    }).error()

    nf = db.select_one("nfs", where={"id": ids["nf_id"]})
    assert nf["status"] == "ERROR"
    assert nf["erro_msg"] == "CNPJ invalido"

    conv = db.select_one("conversations", where={"id": ids["conv_id"]})
    assert conv["status"] == "COLLECTING"


def test_cancelled_marks_nf_cancelled(db):
    ids = _setup_nf(db)

    NfseService({"invoiceId": "inv-123", "cancelledAt": "2026-01-01T00:00:00Z"}).cancelled()

    nf = db.select_one("nfs", where={"id": ids["nf_id"]})
    assert nf["status"] == "CANCELLED"
    assert nf["cancelled_at"] == "2026-01-01T00:00:00Z"


def test_issued_raises_when_invoice_id_unknown(db):
    with pytest.raises(Exception):
        NfseService({"invoiceId": "does-not-exist"}).issued()


def test_ntaas_webhook_parse_rejects_missing_event():
    with pytest.raises(ValueError):
        NtaasWebhook({"data": {}}).parse()


def test_ntaas_webhook_parse_rejects_unknown_event():
    with pytest.raises(ValueError):
        NtaasWebhook({"event": "nfse.made_up", "data": {}}).parse()


def test_ntaas_webhook_parse_accepts_known_event():
    payload = NtaasWebhook({"event": "nfse.issued", "data": {"invoiceId": "inv-123"}}).parse()

    assert payload.event == EventsNotaas.NFSE_ISSUED
    assert payload.data == {"invoiceId": "inv-123"}


@pytest.mark.parametrize("event, method", [
    ("nfse.issued", "issued"),
    ("nfse.error", "error"),
    ("nfse.cancelled", "cancelled"),
    ("nfse.documents_ready", "docs_ready"),
])
def test_ntaas_webhook_dispatch_routes_by_event(monkeypatch, event, method):
    calls = []
    fake_service = type("S", (), {
        "issued": lambda self: calls.append("issued"),
        "error": lambda self: calls.append("error"),
        "cancelled": lambda self: calls.append("cancelled"),
        "docs_ready": lambda self: calls.append("docs_ready"),
    })()
    monkeypatch.setattr("src.services.ntaas.ntaas_service.NfseService", lambda data: fake_service)

    payload = NtaasWebhook({"event": event, "data": {}}).parse()
    NtaasWebhook({}).dispatch(payload)

    assert calls == [method]


def test_ntaas_webhook_dispatch_webhook_test_is_a_noop():
    payload = NtaasWebhook({"event": "webhook.test", "data": {}}).parse()
    assert NtaasWebhook({}).dispatch(payload) is None


def test_docs_ready_stores_pdf_url(db):
    ids = _setup_nf(db)

    NfseService({
        "invoiceId": "inv-123", "documentStatus": "complete", "pdfUrl": "https://notaas/doc.pdf",
    }).docs_ready()

    nf = db.select_one("nfs", where={"id": ids["nf_id"]})
    assert nf["pdf_url"] == "https://notaas/doc.pdf"


def test_docs_ready_does_not_clobber_existing_url_with_null(db):
    ids = _setup_nf(db)
    NfseService({"invoiceId": "inv-123", "pdfUrl": "https://notaas/doc.pdf"}).docs_ready()

    NfseService({"invoiceId": "inv-123", "documentStatus": "partial"}).docs_ready()

    nf = db.select_one("nfs", where={"id": ids["nf_id"]})
    assert nf["pdf_url"] == "https://notaas/doc.pdf"

    NfseService({"invoiceId": "inv-123", "documentStatus": "partial"}).docs_ready()

    nf = db.select_one("nfs", where={"id": ids["nf_id"]})
    assert nf["pdf_url"] == "https://notaas/doc.pdf"

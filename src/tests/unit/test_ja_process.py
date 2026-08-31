from src.services.ntaas.ja_process import ja_process


def test_ja_process_false_na_primeira_vez(db):
    assert ja_process("delivery-abc") is False


def test_ja_process_true_em_entregas_repetidas(db):
    ja_process("delivery-abc")
    assert ja_process("delivery-abc") is True


def test_ja_process_ids_diferentes_sao_independentes(db):
    assert ja_process("delivery-1") is False
    assert ja_process("delivery-2") is False


def test_ja_process_grava_trilha_de_auditoria(db):
    ja_process(
        "delivery-xyz",
        event="nfse.issued",
        invoice_id="inv-99",
        payload_raw=b'{"event":"nfse.issued","data":{"invoiceId":"inv-99"}}',
    )

    row = db.select_one("ntaas_deliveries", where={"delivery_id": "delivery-xyz"})
    assert row["event"] == "nfse.issued"
    assert row["invoice_id"] == "inv-99"
    assert '"invoiceId":"inv-99"' in row["payload"]

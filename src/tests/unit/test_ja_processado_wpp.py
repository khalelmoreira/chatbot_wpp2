from src.services.wpp.ja_processado_service import ja_processado


def test_ja_processado_false_na_primeira_vez(db):
    assert ja_processado("wamid.abc") is False


def test_ja_processado_true_em_mensagens_repetidas(db):
    ja_processado("wamid.abc")
    assert ja_processado("wamid.abc") is True


def test_ja_processado_ids_diferentes_sao_independentes(db):
    assert ja_processado("wamid.1") is False
    assert ja_processado("wamid.2") is False

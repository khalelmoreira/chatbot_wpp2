from src.services.ntaas.ja_process import ja_process


def test_ja_process_false_na_primeira_vez(db):
    assert ja_process("delivery-abc") is False


def test_ja_process_true_em_entregas_repetidas(db):
    ja_process("delivery-abc")
    assert ja_process("delivery-abc") is True


def test_ja_process_ids_diferentes_sao_independentes(db):
    assert ja_process("delivery-1") is False
    assert ja_process("delivery-2") is False

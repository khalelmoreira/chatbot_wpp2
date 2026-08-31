from src.utils.nome_empresa import nome_confere_com_receita, normalizar


def test_normalizar_strips_accents_case_punctuation_and_suffixes():
    assert normalizar("Comércio Silva & Filhos LTDA.") == "silva filhos"
    assert normalizar("PADARIA DO ZE ME") == "padaria do ze"


def test_exact_match_after_normalisation():
    info = {"razao_social": "CLIENTE SILVA LTDA"}
    assert nome_confere_com_receita("Cliente Silva", info)


def test_substring_match_either_direction():
    assert nome_confere_com_receita("Comercial Silva", {"razao_social": "COMERCIAL SILVA E FILHOS LTDA"})
    assert nome_confere_com_receita("Padaria do Ze Materiais", {"nome_fantasia": "PADARIA DO ZE"})


def test_matches_against_nome_fantasia_when_razao_differs():
    info = {"razao_social": "J S COMERCIO DE ALIMENTOS LTDA", "nome_fantasia": "PADARIA DO ZE"}
    assert nome_confere_com_receita("Padaria do Zé", info)


def test_positive_mismatch_is_rejected():
    assert not nome_confere_com_receita("Cliente LTDA", {"razao_social": "OUTRA EMPRESA LTDA"})


def test_fails_open_when_receita_has_no_name():
    assert nome_confere_com_receita("Qualquer Nome", {"descricao_situacao_cadastral": "ATIVA"})


def test_empty_name_is_rejected():
    assert not nome_confere_com_receita("", {"razao_social": "OUTRA EMPRESA LTDA"})

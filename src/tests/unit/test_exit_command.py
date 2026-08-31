import pytest

from src.services.active.exit_command import is_exit_command


@pytest.mark.parametrize("texto", [
    "cancelar", "Cancelar", "CANCELAR", "  cancelar  ", "cancelar.", "cancela",
    "sair", "parar", "desistir", "encerrar",
])
def test_reconhece_palavras_de_saida(texto):
    assert is_exit_command(texto) is True


@pytest.mark.parametrize("texto", [
    None, "", "emite para joão da silva",
    "serviço de cancelamento de contrato",   # 'cancel' como substring não conta
    "quero cancelar a nota do cliente X",     # frase, não a palavra isolada
    "para joão",                              # 'para' preposição, não está na lista
])
def test_ignora_texto_comum(texto):
    assert is_exit_command(texto) is False

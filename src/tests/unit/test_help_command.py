import pytest

from src.services.sign_up.help_command import is_help_command


@pytest.mark.parametrize("texto", [
    "ajuda", "Ajuda", "AJUDA", "  ajuda  ", "ajuda!", "ajuda?", "help", "Help",
])
def test_reconhece_palavras_de_ajuda(texto):
    assert is_help_command(texto) is True


@pytest.mark.parametrize("texto", [
    None, "", "preciso de ajuda com o cadastro",   # frase, não a palavra isolada
    "ajuda de custo",                               # descrição de serviço
    "socorro", "duvida",                            # fora da lista reservada
])
def test_ignora_texto_comum(texto):
    assert is_help_command(texto) is False

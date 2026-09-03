"""Palavra reservada de ajuda: o usuário digita "ajuda" (ou "help") para abrir o
modo assistente — uma conversa livre, alimentada por FAQ, que só explica como o
sistema funciona e não altera nenhum dado.

Espelha a palavra de saída (`exit_command.py`): determinística, sem IA no
caminho, e só dispara quando a mensagem *inteira* é a palavra — senão uma
descrição de serviço como "ajuda de custo" abriria o modo ajuda sem querer.

Diferença em relação à saída: entrar na ajuda é reversível e não-destrutivo. O
`UserStatus` anterior fica guardado em `prestador.help_return_to` e é restaurado
quando o usuário digita uma palavra de saída (`is_exit_command`) — ver
`DispatchUser` e `help_flow`.
"""

from src.utils.text import normalize_word

_HELP_WORDS: frozenset[str] = frozenset({"ajuda", "help"})


def is_help_command(texto: str | None) -> bool:
    if not texto:
        return False
    return normalize_word(texto) in _HELP_WORDS

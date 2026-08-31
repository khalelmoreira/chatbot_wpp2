"""Palavra de saída: o prestador digita "cancelar" (ou similar) para abandonar
uma emissão em andamento — vale só em COLLECTING e CONFIRMING.

Determinístico de propósito: sem IA no caminho, e só dispara quando a mensagem
*inteira* é a palavra, nunca como substring — senão uma descrição de serviço como
"cancelamento de contrato" derrubaria o fluxo.
"""

import unicodedata

_EXIT_WORDS: frozenset[str] = frozenset({
    "cancelar",
    "cancela",
    "sair",
    "parar",
    "desistir",
    "encerrar",
})

# Mensagem única de confirmação do cancelamento — usada pela palavra digitada
# (DispatchActiveService) e pelo botão ❌ Cancelar (ConfirmingService).
EXIT_CONFIRMATION_MSG = (
    "Ok, cancelei esta emissão. Quando quiser emitir uma nota, é só me enviar os dados. 👍"
)


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.casefold().strip(" \t\n.!?")


def is_exit_command(texto: str | None) -> bool:
    if not texto:
        return False
    return _normalizar(texto) in _EXIT_WORDS

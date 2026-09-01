"""Palavra de saída: o usuário digita "cancelar" (ou similar) para abandonar um
fluxo em andamento e voltar ao ponto de partida.

Vale para as duas máquinas de estado conversacionais: a emissão de uma NFS-e
(`ConvStatus`, em COLLECTING/CONFIRMING) e o onboarding do prestador
(`UserStatus`, em qualquer etapa antes de ACTIVE — ver `DispatchUser`). O módulo
mora em `active/` por ser onde o recurso nasceu; o detector em si não tem nada
de específico da emissão.

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

# Confirmação do cancelamento de uma emissão (ConvStatus) — usada pela palavra
# digitada (DispatchActiveService) e pelo botão ❌ Cancelar (ConfirmingService).
EXIT_CONFIRMATION_MSG = (
    "Ok, cancelei esta emissão. Quando quiser emitir uma nota, é só me enviar os dados. 👍"
)

# Confirmação do cancelamento do cadastro (UserStatus) — usada pela palavra
# digitada durante o onboarding (DispatchUser).
SIGNUP_EXIT_CONFIRMATION_MSG = (
    "Ok, cancelei o cadastro. Quando quiser retomar, é só me enviar seus dados. 👍"
)

# Linha em itálico anexada à saudação (idle_flow) para o usuário saber da saída.
EXIT_HINT = '_Durante uma emissão, é só digitar "cancelar" a qualquer momento para desistir._'


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.casefold().strip(" \t\n.!?")


def is_exit_command(texto: str | None) -> bool:
    if not texto:
        return False
    return _normalizar(texto) in _EXIT_WORDS

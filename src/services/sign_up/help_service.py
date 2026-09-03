"""Modo ajuda: uma conversa livre, alimentada pela FAQ (`PREST_HELP_RESP`), que só
explica como o sistema funciona. Não coleta nem altera nenhum dado — a IA aqui
apenas responde.

O usuário entra digitando a palavra reservada `ajuda`/`help` (ver `help_command.py`
e `DispatchUser`); o status vira `HELP` e o status anterior fica em
`prestador.help_return_to`. Continua no modo mandando qualquer mensagem; sai
digitando uma palavra de saída (`is_exit_command`), que restaura o status
anterior.
"""

import logging

from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager
from src.services.active.exit_command import is_exit_command
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.services.sender import get_sender
from src.services.sign_up.greeting_service import GreetingService
from src.types import ContextPrestador, MsgType, PrestRespKey, Role

logger = logging.getLogger(__name__)

_INTRO_MSG = (
    "Modo ajuda 🧭\n\n"
    "Pode me perguntar o que quiser sobre o cadastro e a emissão de notas. "
    "Quando terminar, escreva *sair* para voltar de onde você estava."
)

_SAIR_STAGE_MSG = "Pronto, voltamos de onde você estava. 👍 Pode continuar."

_SAIR_IDLE_MSG = "Combinado! Quando quiser começar, é só tocar no botão abaixo."

_BOTAO_NO_HELP_MSG = "Estamos no modo ajuda — me escreva sua dúvida, ou *sair* para voltar."


class HelpService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.msg = MsgManager(ctx.user)
        self.wpp = get_sender(ctx.user.channel)

    def _notf(self, msg: str) -> None:
        self.msg.save_msg(Role.AI, msg)
        self.wpp.send_msg_text(self.ctx.user.phone, msg)

    def intro(self) -> None:
        self._notf(_INTRO_MSG)

    def quer_sair(self) -> bool:
        return self.ctx.msg_type == MsgType.TEXT and is_exit_command(self.ctx.text)

    def sair(self) -> None:
        return_to = self.prestador.leave_help()
        logger.debug("saindo do modo ajuda: return_to=%s", return_to)

        if return_to is None:
            GreetingService(self.ctx, self.prestador).send_card(_SAIR_IDLE_MSG)
            return

        self._notf(_SAIR_STAGE_MSG)

    def responder(self) -> None:
        if self.ctx.msg_type == MsgType.BUTTON:
            self._notf(_BOTAO_NO_HELP_MSG)
            return

        history = self.msg.get_ai_history()
        response = self.ai_respond(history)
        self._notf(response)

    def ai_respond(self, history) -> str:
        ai = AIService(ai_client_factory.build_ai_client())
        return ai.prest.respond(PrestRespKey.HELP, self.ctx.text, history=history)

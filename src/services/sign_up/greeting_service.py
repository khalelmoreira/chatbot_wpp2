"""Saudação de boas-vindas: o texto da IA para uma mensagem sem intenção
(`PREST_NO_INTENT_RESP`) sai acompanhado de dois botões de ação — "🚀 Começar" e
"📖 Como funciona". Os botões são estáticos (o WhatsApp não aceita botão gerado
dinamicamente) e reaproveitam o padrão de card já usado em `address_service.py`.

Um clique nesses botões chega ao `idle_user_flow` como `MsgType.BUTTON`; este
módulo o intercepta antes do classificador de intenção — um `button_id` nunca
deve virar entrada de `classify()`.
"""

from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager
from src.services.sender import get_sender
from src.types import BotaoId, BotaoResponse, ContextPrestador, MsgType, Role, UserStatus

GREETING_BUTTONS: list[BotaoResponse] = [
    BotaoResponse(id=BotaoId.INICIO_COMECAR, title="🚀 Começar"),
    BotaoResponse(id=BotaoId.INICIO_COMO_FUNCIONA, title="📖 Como funciona"),
]

_COMECAR_BUTTON: list[BotaoResponse] = [
    BotaoResponse(id=BotaoId.INICIO_COMECAR, title="🚀 Começar"),
]

COMO_FUNCIONA_MSG = (
    "Funciona assim: 📋\n\n"
    "1. *Cadastro* (uma vez só) — você me manda numa mensagem: nome da empresa, CNPJ, CEP, "
    "e-mail e regime tributário (ex.: Simples Nacional, MEI).\n"
    "2. Eu confirmo o *endereço* pelo CEP e peço o número.\n"
    "3. Você envia o *certificado digital* (arquivo .pfx) por um link seguro — é o que assina "
    "a nota fiscal.\n"
    "4. Pronto! Para emitir uma nota, me manda os dados do cliente, a descrição do serviço e o "
    "valor. Você confere, confirma, e eu envio para a prefeitura.\n\n"
    "Quando quiser começar, toque no botão abaixo. Dúvidas a qualquer momento? Escreva *ajuda*."
)


class GreetingService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.msg = MsgManager(ctx.user)
        self.wpp = get_sender(ctx.user.channel)

    def send_card(self, body: str) -> None:
        """Envia a saudação (texto já composto pela IA) com os dois botões de ação."""
        self.msg.save_msg(Role.AI, body)
        self.wpp.send_msg_botao(self.ctx.user.phone, body, GREETING_BUTTONS)

    def handle_button(self) -> bool:
        """Trata um clique nos botões da saudação. Retorna True se consumiu a mensagem
        (o chamador deve parar), False se não era um botão de saudação."""
        if self.ctx.msg_type != MsgType.BUTTON:
            return False

        match self.ctx.button_id:
            case BotaoId.INICIO_COMECAR:
                self.prestador.update_state(UserStatus.COLLECTING)
                collecting_flow(self.ctx)
                return True
            case BotaoId.INICIO_COMO_FUNCIONA:
                self._como_funciona()
                return True
            case _:
                return False

    def _como_funciona(self) -> None:
        self.msg.save_msg(Role.AI, COMO_FUNCIONA_MSG)
        self.wpp.send_msg_botao(self.ctx.user.phone, COMO_FUNCIONA_MSG, _COMECAR_BUTTON)

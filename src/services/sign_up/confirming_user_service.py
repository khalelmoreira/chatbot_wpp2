from src.flows.user_flows.project_flow import project_flow
from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager
from src.services.sender import get_sender
from src.types import BotaoId, ContextPrestador, MsgType, Role, UserStatus


class ConfirmUserService:
    def __init__(self, ctx:ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.wpp = get_sender(ctx.user.channel)

    def _notf_user(self, msg: str) -> None:
        self.wpp.send_msg_text(self.ctx.user.phone, msg)

    def dispatch(self):

        if self.ctx.msg_type != MsgType.BUTTON:
            self._use_botoes_msg()
            return
        
        match self.ctx.button_id:
            case BotaoId.PRESTADOR_CONFIRMADO:
                self.prestador.update_state(UserStatus.PROJECT)
                return project_flow(self.ctx)
            
            case BotaoId.PRESTADOR_CORRIGIR:
                self._prestador_corrigir()
                return
            
            case _:
                raise ValueError(f"Button ID não encontrado: {self.ctx.button_id}")

    def _prestador_corrigir(self):
        self.prestador.update_state(UserStatus.ADDRESS)
        msg = "Por favor, digite sem endereço completo."
        self._notf_user(msg)
        MsgManager(self.ctx.user).save_msg(Role.AI, msg)

    def _use_botoes_msg(self):
        msg="Por favor, use os botões para confirmar ou corrigir os dados."
        self._notf_user(msg)
        MsgManager(self.ctx.user).save_msg(Role.AI, msg)
from src.types import ContextPrestador, IncomingMessage, MsgType, Role, BotaoId, UserStatus
from src.managers.prestador_manager import PrestadorManager
from src.services.wpp.msg_service import WhatsAppService
from src.managers.msg_manager import MsgManager

def _notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class ConfirmUserService:
    def __init__(self, ctx:ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.wpp = WhatsAppService()

    def dispatch(self):

        if self.ctx.msg_type != MsgType.BUTTON:
            self._use_botoes_msg()
            return
        
        match self.ctx.button_id:
            case BotaoId.PRESTADOR_CONFIRMADO:
                self._prestador_confirmado()
                return
            
            case BotaoId.PRESTADOR_CORRIGIR:
                self._prestador_corrigir()
                return
            
            case _:
                raise ValueError(f"Button ID não encontrado: {self.ctx.button_id}")

    def _prestador_corrigir(self):
        self.prestador.update_state(UserStatus.COLLECTING)
        msg = "Por favor, digite os dados novamente para podermos continuar"
        _notf_user(msg)
        MsgManager(self.ctx).save_msg(Role.AI, msg)

    def _prestador_confirmado(self):
        self.prestador.update_state(UserStatus.PROJECT)
        
    def _use_botoes_msg(self):
        _notf_user(msg="Por favor, use os botões para confirmar ou corrigir os dados.")
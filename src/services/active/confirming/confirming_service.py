from src.types import IncomingMessage, ContextTomador, ConvStatus, MsgType, BotaoId, Role
from src.managers.conversations.conv_manager import ConvManager
from src.managers.tomador_manager import TomadorManager
from src.services.wpp.msg_service import WhatsAppService
from src.managers.msg_manager import MsgManager

class ConfirmingService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.conversation = conversation
        self.tomador = TomadorManager(ctx)
        self.wpp = WhatsAppService()
        
    def dispatch(self):

        if self.ctx.msg_type != MsgType.BUTTON:
            self._use_botoes_msg()
            return
        
        match self.ctx.button_id:
            case BotaoId.TOMADOR_CONFIRMADO:
                self._tomador_confirmado()
                return
            
            case BotaoId.TOMADOR_CORRIGIR:
                self._tomador_corrigir()
                return
            
            case _:
                raise ValueError(f"Button ID não encontrado: {self.ctx.button_id}")

    def _use_botoes_msg(self):
        self._notf_user(msg="Por favor, use os botões para confirmar ou corrigir os dados.")

    def _tomador_confirmado(self):
        self.conversation.update_state(ConvStatus.QUEUED)
        draft = self.conversation.get_draft()
        
        self.tomador.update_nf_from_draft(draft)
        self._notf_user(msg="Sua nota fiscal já entrou na fila e será emitida em instantes.")

    def _tomador_corrigir(self):
        self.conversation.update_state(ConvStatus.COLLECTING)
        self._notf_user(msg="Por favor, digite os dados do tomador novamente para podermos continuar")

    def _notf_user(self, msg: str) -> None:
        MsgManager(self.ctx).save_msg(Role.AI, msg)
        #self.wpp.send_msg_text(self.msg.phone, msg)
        print(f"{msg}\n")
from src.types import IncomingMessage, ContextTomador
from src.managers.conversations.conversation_manager import ConversationManager
from src.managers.tomador.tomador_manager import TomadorManager
from src.types.conversation_state import ConversationStatus
from src.services.shared.msg_service import WhatsAppService

class ConfirmingService:
    def __init__(self, ctx: ContextTomador, msg: IncomingMessage, conversation: ConversationManager):
        self.ctx = ctx
        self.msg = msg
        self.conversation = conversation
        self.tomador = TomadorManager(ctx)
        self.wpp = WhatsAppService()
        
    def dispatch(self):
        if self.msg.tipo != "button_reply":
            self._use_botoes_msg()
            return
        
        if self.msg.id_botao == "tomador_confirmado":
            self._tomador_confirmado()
            return
        
        if self.msg.id_botao == "tomador_corrigir":
            self._tomador_corrigir()
            return
        
        else:
            return

    def _use_botoes_msg(self):
        self._notf_user(msg="Por favor, use os botões para confirmar ou corrigir o endereço.")

    def _tomador_confirmado(self):

        self.conversation.update_state(ConversationStatus.QUEUED)
        draft = self.conversation.get_draft()
        
        self.tomador.update_nf_from_draft(draft)
        self._notf_user(msg="Sua nota fiscal já entrou na fila e será emitida em instantes.")

    def _tomador_corrigir(self):
        self.conversation.update_state(ConversationStatus.COLLECTING)
        self._notf_user(msg="Por favor, digite os dados do tomador novamente para podermos continuar")

    def _notf_user(self, msg: str) -> None:
        #self.wpp.send_msg_text(self.msg.phone, msg)
        print(f"{msg}\n")
from src.types import IncomingMessage, ContextTomador
from src.managers.conversation_manager import ConversationManager
from src.managers.tomador_manager import TomadorManager
from src.types.conversation_state import ConversationStatus
from src.services.shared.msg_service import WhatsAppService

class ConfirmingService:
    def __init__(self, ctx: ContextTomador, msg: IncomingMessage, conversation: ConversationManager):
        self.ctx = ctx
        self.msg = msg
        self.conversation = conversation
        self.tomador = TomadorManager()
        self.wpp = WhatsAppService()
        
    def parse(self):
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
        #self.wpp.send_msg_text(msg.phone, "Por favor, use os botões para confirmar ou corrigir o endereço.")
        print(f"Por favor, use os botões para confirmar ou corrigir os dados.\n")

    def _tomador_confirmado(self):
        self.conversation.update_state(self.ctx.conversation_id, ConversationStatus.QUEUED)
        draft = self.conversation.get_draft()
        self.tomador.update_nf_from_draft(draft)
        #self.wpp.send_msg_text(ctx.user.phone, "Sua nota fiscal já entrou na fila e será emitida em instantes.")
        print("Sua nota fiscal já entrou na fila e será emitida em instantes.\n")

    def _tomador_corrigir(self):
        self.conversation.update_state(self.ctx.conversation_id, ConversationStatus.COLLECTING)
        # self.wpp.send_msg_text(
        #     msg.text,
        #     "Por favor, digite os dados do tomador novamente para podermos continuar"
        # )
        print("Por favor, digite os dados do tomador novamente para podermos continuar\n")
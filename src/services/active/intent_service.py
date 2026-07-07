from src.types import ContextTomador, IntentTipo, Role
from chatbot_wpp2.src.managers.conversations.conv_manager import ConversationManager
from chatbot_wpp2.src.managers.msg_manager import MsgManager
from src.services.ai.ai_service import AIAssitant
from src.services.onboarding.resumo import ResumoBuilder
from src.flows.active_flows.collecting_flow import collecting_flow

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class IntentService:
    def __init__(self, ctx: ContextTomador, conversation: ConversationManager):
        self.ctx = ctx
        self.conversation = conversation
        self.assistant = AIAssitant(ctx)
        self.resumo = ResumoBuilder(ctx, ctx.conv_status)
        self.msg = MsgManager(ctx)

    def dispatch_intent(self, intencao: IntentTipo):

        match intencao:
            case IntentTipo.EMITIR:
                self.ctx.conversation_id = self.conversation.create_conversation()
                return collecting_flow(self.ctx, self.conversation)
            
            case IntentTipo.CONSULTA:
                self._ref_past()
                return
            
            case IntentTipo.NENHUM:
                self._nenhum()
                return
            
            case _:
                raise ValueError(f"Intenção de usuario não tratada: {intencao}")
            
    def intent(self) -> IntentTipo:
        intencao = self.assistant.classificar_intent()
        print(f"INTENCAO: {intencao}\n")
        return intencao
    
    def _consulta(self):

        resumo_data = self.resumo.resumo_status()
        print(f"RESUMO: {resumo_data}\n")

        response = self.assistant.status_response(resumo_data)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)
    
    def _ref_past(self):
        nfs_history = self.resumo.resumo_nfs_history()
        msgs_history = self.resumo.resumo_msg_history()
        print(f"NFS_HISTORY: {nfs_history}\n")
        print(f"MSGS_HISTORY: {msgs_history}\n")

        response = self.assistant.history_response(nfs_history, msgs_history)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)

    def _nenhum(self):
        response = self.assistant.no_intent_response()
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)

    def _no_intent(self):
        response = self.assistant.no_intent_response()
        #self.wpp.send_msg_text(self.ctx.user.phone, response)
        print(f"RESPONSE: {response}\n")
        return False
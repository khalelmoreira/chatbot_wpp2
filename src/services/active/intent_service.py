from src.types import ContextTomador, IntentType, Role
from src.managers.conversations.conv_manager import ConvManager
from src.managers.msg_manager import MsgManager
from src.services.ai.ai_service import AIService
from src.services.onboarding.resumo import ResumoBuilder
from src.flows.active_flows.collecting_flow import collecting_flow

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class IntentService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.conversation = conversation
        self.ai = AIService()
        self.resumo = ResumoBuilder(ctx, ctx.conv_status)
        self.msg = MsgManager(ctx)

    def dispatch_intent(self, intencao: IntentType):

        match intencao:
            case IntentType.EMITIR:
                self.ctx.conv_id = self.conversation.create_conversation()
                return collecting_flow(self.ctx, self.conversation)
            
            case IntentType.CONSULTA:
                self._ref_past()
                return
            
            case IntentType.NENHUM:
                self._nenhum()
                return
            
            case _:
                raise ValueError(f"Intenção de usuario não tratada: {intencao}")
            
    def intent(self) -> IntentType:
        intencao = self.ai.classificar_intent()
        print(f"INTENCAO: {intencao}\n")
        return intencao
    
    def _consulta(self):

        resumo_data = self.resumo.resumo_status()
        print(f"RESUMO: {resumo_data}\n")

        response = self.ai.status_response(resumo_data)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)
    
    def _ref_past(self):
        nfs_history = self.resumo.resumo_nfs_history()
        msgs_history = self.resumo.resumo_msg_history()
        print(f"NFS_HISTORY: {nfs_history}\n")
        print(f"MSGS_HISTORY: {msgs_history}\n")

        response = self.ai.history_response(nfs_history, msgs_history)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)

    def _nenhum(self):
        response = self.ai.no_intent_response(self.ctx)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)
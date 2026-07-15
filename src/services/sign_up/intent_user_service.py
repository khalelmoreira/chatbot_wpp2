from src.types import ContextTomador, IntentUserType, Role, UserStatus
from src.managers.msg_manager import MsgManager
from src.managers.prestador_manager import PrestadorManager
from src.services.ai.ai_service import AIService
from src.services.onboarding.resumo import ResumoBuilder
from src.flows.user_flows.collecting_user_flow import collecting_flow

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class IntentUserService:
    def __init__(self, ctx: ContextTomador):
        self.ctx = ctx
        self.ai = AIService()
        self.prestador = PrestadorManager(ctx)
        self.msg = MsgManager(ctx)

    def dispatch_intent(self, intencao: IntentUserType):

        match intencao:
            case IntentUserType.ONBOARDING:
                self.prestador.update_state(UserStatus.COLLECTING)
                return collecting_flow(self.ctx, manager)
            
            case IntentUserType.GENERAL_ASK:
                self._general_ask()
                return
            
            case IntentUserType.NENHUM:
                self._nenhum()
                return
            
            case _:
                raise ValueError(f"Intenção de usuario não tratada: {intencao}")
            
    def intent(self) -> IntentUserType:
        intencao = self.ai.classificar_intent_user(self.ctx)
        print(f"INTENCAO: {intencao}\n")
        return intencao
    
    def _general_ask(self):
        response = self.ai.general_ask(self.ctx)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)

    def _nenhum(self):
        response = self.ai.no_intent_prest(self.ctx)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)
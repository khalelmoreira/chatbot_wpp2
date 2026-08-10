from typing import cast

from src.services.ai import ai_client_factory
from src.types import ContextPrestador, IntentUserType, Role, UserStatus, PrestClassKey, PrestRespKey
from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager
from src.services.ai.ai_service import AIService
from src.flows.user_flows.collecting_user_flow import collecting_flow

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class IntentUserService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.msg = MsgManager(ctx)

    def dispatch_intent(self, intencao: IntentUserType):

        match intencao:
            case IntentUserType.ONBOARDING:
                self.prestador.update_state(UserStatus.COLLECTING)
                return collecting_flow(self.ctx)
            
            case IntentUserType.GENERAL_ASK:
                self._general_ask()
                return
            
            case IntentUserType.NENHUM:
                self._nenhum()
                return
            
            case _:
                raise ValueError(f"Intenção de usuario não tratada: {intencao}")
            
    def intent(self) -> IntentUserType:
        intencao = cast(
            IntentUserType,
            self.ai.prest.classify(PrestClassKey.HAS_INTENT, self.ctx.text))
        print(f"INTENCAO: {intencao}\n")
        return intencao
    
    def _general_ask(self):
        response = self.ai.prest.respond(PrestRespKey.GENERAL_ASK, self.ctx.text)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)

    def _nenhum(self):
        response = self.ai.prest.respond(PrestRespKey.NO_INTENT, self.ctx.text)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)
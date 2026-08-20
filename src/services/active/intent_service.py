import logging
from typing import cast

from src.flows.active_flows.collecting_flow import collecting_flow
from src.managers.conversations.conv_manager import ConvManager
from src.managers.msg_manager import MsgManager
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.services.onboarding.resumo import ResumoBuilder
from src.types import ContextTomador, IntentType, Role, TomClassKey, TomRespKey

logger = logging.getLogger(__name__)

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class IntentService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.conversation = conversation
        self.ai = AIService(ai_client_factory.build_ai_client())
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
        intencao = cast(
            IntentType,
            self.ai.tom.classify(TomClassKey.HAS_INTENT, self.ctx.text))
        logger.debug("intencao=%s", intencao)
        return intencao
    
    def _consulta(self):
        resumo_data = self.resumo.resumo_status()
        resumo_str = resumo_data.to_str()

        response = self.ai.tom.respond(TomRespKey.ONBOARD_INFO, self.ctx.text, [resumo_str])
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)
    
    def _ref_past(self):
        nfs = self.resumo.resumo_nfs_history()
        nfs_str = "\n\n".join(nf.to_str() for nf in nfs) or "Nenhuma nota recente."

        msgs = self.resumo.resumo_msg_history()
        msgs_str = "\n".join(msg.to_str() for msg in msgs) or "Nenhum historico de conversa."

        response = self.ai.tom.respond(TomRespKey.ONBOARD_HISTORY, self.ctx.text, [nfs_str, msgs_str])
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)

    def _nenhum(self):
        response = self.ai.tom.respond(TomRespKey.NO_INTENT, self.ctx.text)
        self.msg.save_msg(role=Role.AI, content=response)
        notf_user(response)
import logging
from typing import cast

from src.flows.user_flows.collecting_user_flow import collecting_flow
from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.services.sign_up.greeting_service import GreetingService
from src.types import (
    ContextPrestador,
    PrestClassKey,
    PrestRespKey,
    UserStatus,
)

logger = logging.getLogger(__name__)

class IntentUserService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.msg = MsgManager(ctx.user)
        self.history = self.msg.get_ai_history()

    def dispatch_intent(self, quer_cadastrar: bool):
        if quer_cadastrar:
            self.prestador.update_state(UserStatus.COLLECTING)
            return collecting_flow(self.ctx)

        return self._nenhum()

    def intent(self) -> bool:
        quer_cadastrar = cast(
            bool,
            self.ai.prest.classify(PrestClassKey.HAS_INTENT, self.ctx.text, history=self.history))
        logger.debug("quer_cadastrar=%s", quer_cadastrar)
        return quer_cadastrar

    def _nenhum(self):
        response = self.ai.prest.respond(PrestRespKey.NO_INTENT, self.ctx.text, history=self.history)
        GreetingService(self.ctx, self.prestador).send_card(response)

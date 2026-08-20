import logging

from src.managers.user_manager import PrestadorManager
from src.services.sign_up.intent_user_service import IntentUserService
from src.types import ContextPrestador

logger = logging.getLogger(__name__)

def idle_user_flow(ctx: ContextPrestador):

    logger.debug("idle_user_flow: user_id=%s", ctx.user.id)

    conv = PrestadorManager(ctx)
    intent = IntentUserService(ctx, conv)

    intencao = intent.intent()
    intent.dispatch_intent(intencao)
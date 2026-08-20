import logging

from src.managers.conversations import ConvManager
from src.services.active.intent_service import IntentService
from src.types import ContextTomador

logger = logging.getLogger(__name__)

def idle_flow(ctx: ContextTomador, conversation: ConvManager):

    logger.debug("idle_flow: phone=%s", ctx.user.phone)

    intent = IntentService(ctx, conversation)
    intencao = intent.intent()
    intent.dispatch_intent(intencao)
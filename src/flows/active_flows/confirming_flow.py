import logging

from src.managers.conversations.conv_manager import ConvManager
from src.services.active.confirming.confirming_service import ConfirmingService
from src.types import ContextTomador

logger = logging.getLogger(__name__)

def confirming_flow(ctx: ContextTomador, conversation: ConvManager) -> None:

    logger.debug("confirming_flow: phone=%s conv_id=%s", ctx.user.phone, ctx.conv_id)

    confirming = ConfirmingService(ctx, conversation)
    confirming.dispatch()
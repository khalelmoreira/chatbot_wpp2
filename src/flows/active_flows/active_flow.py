import logging

from src.services.active.active_service import ConvActiveService, DispatchActiveService
from src.types import ContextTomador

logger = logging.getLogger(__name__)

def active_flow(ctx: ContextTomador):

    logger.debug("active_flow: phone=%s", ctx.user.phone)

    conv = ConvActiveService(ctx)
    dispatch = DispatchActiveService(ctx)

    conversa = conv.tem_conv()
    dispatch.dispatch(conversa)
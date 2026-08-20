import logging

from src.managers.conversations.conv_manager import ConvManager
from src.services.active.collecting.collecting_service import ExtractionService, ValidationService
from src.types import ContextTomador

logger = logging.getLogger(__name__)

def collecting_flow(ctx: ContextTomador, conversation: ConvManager) -> None:

    logger.debug("collecting_flow: phone=%s conv_id=%s", ctx.user.phone, ctx.conv_id)

    ExtractionService(ctx, conversation).extract_e_merge()
    ValidationService(ctx, conversation).valido_e_completo()
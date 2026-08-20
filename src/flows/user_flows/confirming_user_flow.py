import logging

from src.managers.user_manager import PrestadorManager
from src.services.sign_up.confirming_user_service import ConfirmUserService
from src.types import ContextPrestador

logger = logging.getLogger(__name__)

def confirming_flow(ctx: ContextPrestador) -> None:

    logger.debug("confirming_user_flow: user_id=%s", ctx.user.id)

    prestador = PrestadorManager(ctx)
    ConfirmUserService(ctx, prestador).dispatch()
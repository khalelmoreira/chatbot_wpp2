import logging

from src.managers.user_manager import PrestadorManager
from src.services.sign_up.help_service import HelpService
from src.types import ContextPrestador

logger = logging.getLogger(__name__)

def help_flow(ctx: ContextPrestador, intro: bool = False):

    logger.debug("help_flow: user_id=%s intro=%s", ctx.user.id, intro)

    svc = HelpService(ctx, PrestadorManager(ctx))

    if intro:
        return svc.intro()

    if svc.quer_sair():
        return svc.sair()

    return svc.responder()

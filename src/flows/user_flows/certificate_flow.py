import logging

from src.managers.user_manager import PrestadorManager
from src.services.sign_up.certificate_service import CertificateService
from src.types import ContextPrestador

logger = logging.getLogger(__name__)

def cerfiticate_flow(ctx: ContextPrestador):

    logger.debug("certificate_flow: user_id=%s", ctx.user.id)

    CertificateService(PrestadorManager(ctx)).certificate()

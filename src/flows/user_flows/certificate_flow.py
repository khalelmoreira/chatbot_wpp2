import logging
from src.types import ContextPrestador, IncomingMessage
from src.services.sign_up.certificate_service import CertificateService

logger = logging.getLogger(__name__)

def cerfiticate_flow(ctx: ContextPrestador, msg: IncomingMessage):
    CertificateService().certificate()
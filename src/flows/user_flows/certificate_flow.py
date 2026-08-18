import logging

from src.managers.user_manager import PrestadorManager
from src.services.sign_up.certificate_service import CertificateService
from src.types import ContextPrestador

logger = logging.getLogger(__name__)

def cerfiticate_flow(ctx: ContextPrestador):

    print("\n\n----------------CERTIFICATE FLOW----------------\n\n")

    CertificateService(PrestadorManager(ctx)).certificate()

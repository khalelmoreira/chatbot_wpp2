import logging
from src.types import ContextPrestador
from src.managers.user_manager import PrestadorManager
from src.services.sign_up.certificate_service import CertificateService

logger = logging.getLogger(__name__)

def cerfiticate_flow(ctx: ContextPrestador):

    print(f"\n\n----------------CERTIFICATE FLOW----------------\n\n")

    CertificateService(PrestadorManager(ctx)).certificate()

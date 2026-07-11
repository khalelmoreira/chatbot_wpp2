import os
import httpx
from cryptography.fernet import Fernet
import logging
from src.types import ContextPrestador, CnpjJaCadastradoError, LimitePlanoAtingidoError, DadosInvalidosError, UserStatus, NtaasCertificadoError, IncomingMessage
from chatbot_wpp2.src.services.sign_up.ntaas_org_service import NtaasProject
from src.managers.prestador_manager import PrestadorManager
from src.managers.tokens_manager import TokensManager
from src.models.urls import NOTAAS_BASE_URL
from chatbot_wpp2.src.services.notaas.upload_certificate import send_certificado_ntaas

logger = logging.getLogger(__name__)

def project_flow(ctx: ContextPrestador, msg: IncomingMessage, prestador: PrestadorManager):
        
    nts = NtaasProject(ctx)

    try:
        project_id = nts.create_project(os.environ["NTAAS_ORG_TOKEN"])

    except CnpjJaCadastradoError as e:
        project_id = e.existing_project_id
    
    except (LimitePlanoAtingidoError, DadosInvalidosError) as e:
        prestador.update_error(UserStatus.ERROR, str(e))
        raise

    prestador.update_project_id(project_id, UserStatus.CERTIFICATE)
import os
import httpx
from cryptography.fernet import Fernet
import logging
from src.types import ContextPrestador, CnpjJaCadastradoError, LimitePlanoAtingidoError, DadosInvalidosError, UserStatus, NtaasCertificadoError
from src.services.notaas.ntaas_org_service import NtaasProject
from src.managers.prestador_manager import PrestadorManager
from src.managers.tokens_manager import TokensManager
from src.models.urls import NOTAAS_BASE_URL
from src.services.notaas.formulario import send_certificado_ntaas

logger = logging.getLogger(__name__)

class ProjectOnboarding:
    def __init__(self, ctx: ContextPrestador):
        self.ctx = ctx
        self.validated = ctx.validated
        self.nts = NtaasProject(ctx)
        self.prestador = PrestadorManager(ctx)
        self.token = TokensManager()
    
    def process_project(self):
        try:
            project_id = self.nts.create_project(os.environ["NTAAS_ORG_TOKEN"])

        except CnpjJaCadastradoError as e:
            project_id = e.existing_project_id
        
        except (LimitePlanoAtingidoError, DadosInvalidosError) as e:
            self.prestador.update_error(UserStatus.ERROR, str(e))
            raise

        self.prestador.update_project_id(project_id, UserStatus.CERTIFICATE)

    def receive_certificate(self, token: str, certificate_bytes: bytes, senha: str) -> dict:
        row = self.token.update_used(token)
        if not row:
            raise NtaasCertificadoError("Token de upload inválido, expirado ou já utilizado.")
        
        project = self.prestador.get_project_id()
        if not project:
            raise NtaasCertificadoError("Prestador não está na etapa de certificado.")
        
        return self.send_persist_certificate(project, certificate_bytes, senha)
    
    def send_persist_certificate(self, project_id: str, certificado_bytes: bytes, senha: str) -> dict:
        org_token = os.environ["NTAAS_ORG_TOKEN"]

        try:
            cert_result = send_certificado_ntaas(project_id, certificado_bytes, senha)
        except NtaasCertificadoError as e:
            raise

        api_key_resp = httpx.post(
            f"{NOTAAS_BASE_URL}/org/projects/{project_id}/api-keys",
            json={"name": f"Prestador {self.ctx.user.id}"},
            headers={"x-api-key": org_token},
            timeout=15.0,
        )

        api_key_resp.raise_for_status()
        raw_key = api_key_resp.json()["key"]

        try:
            encrypted_key = fernet_encrypt(raw_key)
        except Exception:
            logger.critical(
                "Falha ao persistir notaas_api_key para prestador_id=%s ap[oacutes] "
                "criação bem-sucedida na Notaas. Revogar manualmente.", self.ctx.user.id
            )
            raise

        row = self.prestador.update_api_key(encrypted_key, UserStatus.ACTIVE)
        if not row:
            logger.warning("prestador_id=%s saiu de CERTIFICATE antes da persistência da api-key.", self.ctx.user.id)

        return cert_result
import os
import httpx
import logging
from src.types import NtaasCertificadoError
from src.managers.tokens_manager import TokensManager
from src.services.wpp.msg_service import WhatsAppService
from src.models.urls import NOTAAS_BASE_URL
from src.services.notaas.upload_certificate import gen_upload_token

logger = logging.getLogger(__name__)

def _notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class CertificateService:
    def __init__(self, org_token):
        self.org_token = org_token

    def certificate(self):
        token = gen_upload_token(prestador_id)
        url = f"{DOMAIN}/upload-certificate/{token}"
        _notf_user(f"Envie seu certificado digital (.pfx) neste link abaixo: {url}\n")
        _notf_user("O link expira em 15 minutos.")

    def send_e_persist_certificate(self):
        try:
            cert_result = self.send_certificado_ntaas(project_id, certificado_bytes, senha)
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

    def receive_certificate(self, token: str, certificate_bytes: bytes, senha: str) -> dict:
        row = self.token.update_used(token)
        if not row:
            raise NtaasCertificadoError("Token de upload inválido, expirado ou já utilizado.")
        
        project = self.prestador.get_project_id()
        if not project:
            raise NtaasCertificadoError("Prestador não está na etapa de certificado.")
        
        return self.send_persist_certificate(project, certificate_bytes, senha)

    def send_certificado_ntaas(self, project_id: str, certificado_bytes: bytes, senha: str) -> dict:
        
        files = {"file": ("certificado.pfx", certificado_bytes, "application/x-pkcs12")}
        data = {"password": senha}
        headers = {"x-api-key": self.org_token}

        resp = httpx.post(
            f"{NOTAAS_BASE_URL}/org/projects/{project_id}/certificate",
            files=files,
            data=data,
            headers=headers,
            timeout=20.0,   
        )

        if resp.status_code in (401, 403):
            raise NtaasCertificadoError(f"org token inválido/sem permissão: {resp.status_code}")
        
        if resp.status_code == 400:
            raise NtaasCertificadoError("Senha do certificado incorreta ou arquivo inválido.")
        
        if resp.status_code == 413:
            raise NtaasCertificadoError("certificado excede 50KB")
        
        resp.raise_for_status()
        return resp.json()
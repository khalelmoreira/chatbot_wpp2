import os
import httpx
import logging
from src.types import NtaasCertificadoError, UserStatus
from src.managers.user_manager import PrestadorManager
from src.services.ntaas.upload_certificate import gen_upload_token
from src.models.urls import NOTAAS_BASE_URL
from src.utils.crypto import fernet_encrypt

logger = logging.getLogger(__name__)

def _notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class CertificateService:
    def __init__(self, prestador: PrestadorManager):
        self.prestador = prestador
        self.org_token = os.environ["NTAAS_ORG_TOKEN"]

    def certificate(self) -> None:
        project_id = self.prestador.get_project_id()
        if project_id is None:
            raise NtaasCertificadoError("Prestador não está na etapa de certificado.")

        token = gen_upload_token(self.prestador.id, project_id)
        url = f"{os.environ['APP_DOMAIN']}/upload-certificate/{token}"
        _notf_user(f"Envie seu certificado digital (.pfx) neste link abaixo: {url}\n")
        _notf_user("O link expira em 15 minutos.")

    def send_e_persist_certificate(self, certificado_bytes: bytes, senha: str) -> dict:
        project_id = self.prestador.get_project_id()
        if project_id is None:
            raise NtaasCertificadoError("Prestador não está na etapa de certificado.")

        cert_result = self._send_certificado_ntaas(project_id, certificado_bytes, senha)

        api_key_resp = httpx.post(
            f"{NOTAAS_BASE_URL}/org/projects/{project_id}/api-keys",
            json={"name": f"Prestador {self.prestador.id}"},
            headers={"x-api-key": self.org_token},
            timeout=15.0,
        )

        api_key_resp.raise_for_status()
        raw_key = api_key_resp.json()["key"]

        try:
            encrypted_key = fernet_encrypt(raw_key)
        except Exception:
            logger.critical(
                "Falha ao persistir notaas_api_key para prestador_id=%s após "
                "criação bem-sucedida na Notaas. Revogar manualmente.", self.prestador.id
            )
            raise

        row = self.prestador.update_api_key(encrypted_key, UserStatus.ACTIVE)
        if row is None:
            logger.warning("prestador_id=%s saiu de CERTIFICATE antes da persistência da api-key.", self.prestador.id)

        return cert_result

    def _send_certificado_ntaas(self, project_id: str, certificado_bytes: bytes, senha: str) -> dict:

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

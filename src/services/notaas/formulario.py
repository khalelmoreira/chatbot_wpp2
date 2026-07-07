import secrets
import os
import httpx
from datetime import datetime, timedelta, timezone
from src.managers.tokens_manager import UploadTokensManager as TokensManager

def gen_upload_token(project_id: int, ttl_min: int = 15) -> str:

    token = secrets.token_urlsafe(32)
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_min)

    TokensManager().insert_token(token, project_id, expire_at)
    return token

class NotaasCertificadoError(Exception):
    pass

def send_certificado_ntaas(
        project_id: str,
        certificado_bytes: bytes,
        senha: str
) -> dict:
    
    org_token = PrestadorManager().get_org_token()
    
    files = {
        "file": ("certificado.pfx", certificado_bytes, "application/x-pkcs12"),
    }
    data = {"password": senha}
    headers = {"x-api-key": org_token}

    resp = httpx.post(
        f"https://platform.notaas.com.br/api/v1/org/projects/{project_id}/certificate",
        files=files,
        data=data,
        headers=headers,
        timeout=20.0,   
    )

    if resp.status_code in (401, 403):
        raise NotaasCertificadoError(f"org token inválido/sem permissão: {resp.status_code}")
    
    if resp.status_code == 413:
        raise NotaasCertificadoError("certificado excede 50KB")
    
    resp.raise_for_status()
    return resp.json()
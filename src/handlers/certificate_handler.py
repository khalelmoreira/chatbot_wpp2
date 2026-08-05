from src.managers.tokens_manager import TokensManager
from src.managers.user_manager import PrestadorManager
from src.services.sign_up.certificate_service import CertificateService
from src.services.ntaas.upload_certificate import expirado
from src.types.exceptions import NtaasCertificadoError
from src.types import HandlerResult

def certificate_form_handler(token: str) -> HandlerResult:

    row = TokensManager().get_token(token)
    if not row or row["used"] or expirado(row["expire_at"]):
        return HandlerResult(410, {"success": False})
    return HandlerResult(200, {"success": True})

def certificate_upload_handler(token: str, arq, pasw: str | None) -> HandlerResult:

    row = TokensManager().get_token(token)
    if not row or row["used"] or expirado(row["expire_at"]):
        return HandlerResult(410, {"error": "token inválido, expirado ou já usado"})

    if not arq or not pasw:
        return HandlerResult(409, {"error": "certificado e senha obrigatorios"})

    prestador = PrestadorManager.for_id(row["prestador_id"])

    certificate_bytes = arq.read()
    try:
        CertificateService(prestador).send_e_persist_certificate(certificate_bytes, pasw)

    except NtaasCertificadoError as e:
        return HandlerResult(400, {"error": str(e)})

    finally:
        del certificate_bytes
        del pasw

    used_row = TokensManager().update_used(token)
    if used_row is None:
        return HandlerResult(410, {"error": "token expirou durante o processamento"})
    return HandlerResult(200, {"success": True})

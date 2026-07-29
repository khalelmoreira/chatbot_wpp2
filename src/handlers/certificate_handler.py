from src.managers.tokens_manager import TokensManager
from src.managers.user_manager import PrestadorManager
from src.services.sign_up.certificate_service import CertificateService
from src.types.exceptions import NtaasCertificadoError
from src.types import HandlerResult

def certificate_form_handler(token: str) -> HandlerResult:

    row = TokensManager().get_token(token)
    if not row or row["used"] or expired(row["expire_at"]):
        return HandlerResult(410, {"success": False})
    return HandlerResult(200, {"success": True})

def certificate_upload_handler(token: str, arq, pasw: str | None) -> HandlerResult:

    row = TokensManager().get_token(token)
    if not row or row["used"] or expired(row["expire_at"]):
        return HandlerResult(410, {"error": "token inválido, expirado ou já usado"})

    prestador = PrestadorManager().get_project_id(row["prestador_id"])
    if not prestador:
        return HandlerResult(409, {"error": "prestador_id não encontrado"})

    if not arq or not pasw:
        return HandlerResult(409, {"error": "certificado e senha obrigatorios"})

    certificate_bytes = arq.read()
    try:
        CertificateService().send_e_persist_certificate(prestador, certificate_bytes, pasw)

    except NtaasCertificadoError as e:
        return HandlerResult(400, {"error": str(e)})

    finally:
        del certificate_bytes
        del pasw

    TokensManager().update_used(token)
    return HandlerResult(200, {"success": True})
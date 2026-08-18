from src.services.validators.security_service import validate_signature


class WebhookValidatorService:
    def validar(self, payload_raw: bytes, signature: str | None) -> tuple[bool, str | None]:
        if not signature:
            return False, "assinatura ausente"

        if not validate_signature(payload_raw, signature):
            return False, "assinatura invalida"

        return True, None
import logging
import json
from src.types import HandlerResult
from src.services.ntaas.ntaas_service import NtaasWebhook
from src.services.ntaas.webhook_validator_service import WebhookValidatorService
from src.services.ntaas.ja_process import ja_process

logger = logging.getLogger(__name__)

def ntaas_handler(payload_raw: bytes, signature: str | None, delivery_id: str | None) -> HandlerResult:

    valid, error = WebhookValidatorService().validar(payload_raw, signature)
    if not valid:
        logger.warning(f"webhook ntaas rejeitado: {error}")
        return HandlerResult(401, {"success": False, "error": error})

    if not delivery_id:
        return HandlerResult(200, {"success": True})

    if ja_process(delivery_id):
        return HandlerResult(200, {"success": True})

    payload = json.loads(payload_raw)

    try:
        nt = NtaasWebhook(payload)
        parsed = nt.parse()
        nt.dispatch(parsed)
        
    except Exception as e:
        logger.exception(f"erro ao proessar webhook notaas: {e}")

    return HandlerResult(200, {"success": True})
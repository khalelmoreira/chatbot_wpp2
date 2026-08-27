from src.services.telegram.msg_service import TelegramService
from src.services.wpp.msg_service import WhatsAppService


def get_sender(channel: str | None) -> WhatsAppService | TelegramService:
    """Escolhe o serviço de envio pelo canal do usuário. `None` (dado legado
    de antes do Telegram existir) cai em WhatsApp — era o único canal até aqui."""
    if channel == "TELEGRAM":
        return TelegramService()
    return WhatsAppService()

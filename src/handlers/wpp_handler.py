import logging

from src.handlers.initial_handler import initial_handler
from src.managers.user_manager import UserManager
from src.services.errors.error_notifier import notificar_erro_processamento
from src.services.wpp.debounce_service import buffer_message
from src.services.wpp.ja_processado_service import ja_processado
from src.services.wpp.user_lock_service import with_user_lock
from src.services.wpp.wpp_parser_service import WppParser
from src.types import IncomingMessage

logger = logging.getLogger(__name__)


def wpp_handler(payload_raw) -> None:
    parser = WppParser(payload_raw)

    msg = parser.parse()
    if msg is None:
        return
    logger.debug("wpp_handler: msg=%s", msg)

    if ja_processado(msg.msg_id):
        logger.info("mensagem duplicada ignorada: msg_id=%s phone=%s", msg.msg_id, msg.phone)
        return

    buffer_message(msg, on_flush=_process)

def _process(msg: IncomingMessage) -> None:
    with with_user_lock(msg.phone):
        try:
            initial_handler(msg)
        except Exception as e:
            user = UserManager().get_user(msg.phone)
            notificar_erro_processamento(user.id if user else None, msg.phone, e)
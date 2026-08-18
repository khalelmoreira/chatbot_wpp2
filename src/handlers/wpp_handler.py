from src.handlers.initial_handler import initial_handler
from src.services.wpp.debounce_service import buffer_message
from src.services.wpp.user_lock_service import with_user_lock
from src.services.wpp.wpp_parser_service import WppParser
from src.types import IncomingMessage


def wpp_handler(payload_raw) -> None:
    print("\n\n----------------TESTE PROCESSAMENTO PAYLOAD WHATSAPP----------------\n\n")

    parser = WppParser(payload_raw)

    msg = parser.parse()
    if msg is None:
        return
    print(f"msg: {msg}\n")

    buffer_message(msg, on_flush=_process)

def _process(msg: IncomingMessage) -> None:
    with with_user_lock(msg.phone):
        initial_handler(msg)
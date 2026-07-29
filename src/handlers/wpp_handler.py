from src.handlers.initial_handler import initial_handler
from src.services.wpp.wpp_parser_service import WppParser

def wpp_handler(payload_raw) -> None:
    print(f"\n\n----------------TESTE PROCESSAMENTO PAYLOAD WHATSAPP----------------\n\n")

    parser = WppParser(payload_raw)

    msg = parser.parse()
    if msg is None:
        return
    print(f"msg: {msg}\n")
    
    initial_handler(msg)
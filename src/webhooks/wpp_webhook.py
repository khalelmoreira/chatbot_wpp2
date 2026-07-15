from typing import Any
from dotenv import load_dotenv
from src.flows.initial_flow import initial_flow
from src.services.wpp.webhook_parser_service import WhatsappWebhookParser
from src.managers.msg_manager import MsgManager
# from src.repositories.message_repo import salvar_msg_se_nova

load_dotenv()

class WppWebhook:
    def __init__(self, payload_raw):
        self.payload_raw = payload_raw

    def wpp_webhook(self) -> Any:

        print(f"\n\n----------------TESTE PROCESSAMENTO PAYLOAD WHATSAPP----------------\n\n")
        parser = WhatsappWebhookParser(self.payload_raw)

        msg = parser.parse()
        print(f"msg: {msg}\n")
        
        initial_flow(msg)

        # fila.enqueue(
        #     fluxo_principal,
        #     msg
        # )


# def mensagem_nova(msg: IncomingMessage) -> Optional[Any]:
    
#     return salvar_msg_se_nova(
#         phone=msg.phone,
#         tipo=msg.tipo,
#         mensagem_id=msg.msg_id,
#         conteudo=msg.text,
#         timestamp=msg.timestamp
#     )

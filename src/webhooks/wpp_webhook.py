from typing import Any
from dotenv import load_dotenv
from src.flows.initial_flow import initial_flow
from src.services.wpp.webhook_parser_service import WhatsappWebhookParser
# from src.repositories.message_repo import salvar_msg_se_nova

load_dotenv()

def wpp_webhook(payload) -> Any:

    print(f"\n\n----------------TESTE PROCESSAMENTO PAYLOAD WHATSAPP----------------\n\n")
    parser = WhatsappWebhookParser()

    msg = parser.parse(payload)
    print(f"msg: {msg}\n")
    
    # mensagem_nova(msg)
    print(f"processou webhook\ndados msg: {msg}\n")


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

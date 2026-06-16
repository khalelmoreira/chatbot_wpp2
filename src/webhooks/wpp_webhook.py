from typing import Optional, Any
from dotenv import load_dotenv
from chatbot_wpp2.src.flows.initial_flow import fluxo_principal
from src.types.incoming_msg import IncomingMessage
from chatbot_wpp2.src.services.wpp.webhook_parser_service import WhatsappWebhookParser
# from src.repositories.message_repo import salvar_msg_se_nova

load_dotenv()

def wpp_webhook(payload) -> Any:

    print(f"\n\n----------------TESTE PROCESSAMENTO PAYLOAD WHATSAPP----------------\n\n")

    print(f"\nrecebeu payload: {payload}\n")

    parser = WhatsappWebhookParser()

    ctx_meta = parser.parse(payload)

    print(f"ctx_meta: {ctx_meta}\n")
    
    # mensagem_nova(ctx_meta)

    print(f"processou webhook\ndados msg: {ctx_meta}\n")


    fluxo_principal(ctx_meta)

    # fila.enqueue(
    #     fluxo_principal,
    #     ctx_meta
    # )


# def mensagem_nova(ctx_meta: IncomingMessage) -> Optional[Any]:
    
#     return salvar_msg_se_nova(
#         phone=ctx_meta.phone,
#         tipo=ctx_meta.tipo,
#         mensagem_id=ctx_meta.msg_id,
#         conteudo=ctx_meta.text,
#         timestamp=ctx_meta.timestamp
#     )

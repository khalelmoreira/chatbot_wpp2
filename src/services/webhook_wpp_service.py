from typing import Optional, Any
from dotenv import load_dotenv
from src.flows.fluxo_principal import fluxo_principal
from src.services.fila_service import fila
from src.repositories.message_db import salvar_msg_se_nova
from src.types.incoming_msg import IncomingMessage
from src.services.webhook_parser_service import WhatsappWebhookParser

load_dotenv()

def processar_webhook(payload) -> Any:

    print(f"\n\n----------------TESTE PROCESSAMENTO PAYLOAD WHATSAPP----------------\n\n")

    print(f"\nrecebeu payload: {payload}\n")

    parser = WhatsappWebhookParser()

    ctx_meta = parser.parse(payload)

    print(f"ctx_meta: {ctx_meta}\n")
    
    mensagem_nova(ctx_meta)

    print(f"processou webhook\ndados msg: {ctx_meta}\n")


    fluxo_principal(ctx_meta)

    # fila.enqueue(
    #     fluxo_principal,
    #     ctx_meta
    # )


def mensagem_nova(ctx_meta: IncomingMessage) -> Optional[Any]:
    
    return salvar_msg_se_nova(
        phone=ctx_meta.phone,
        tipo=ctx_meta.tipo,
        mensagem_id=ctx_meta.msg_id,
        conteudo=ctx_meta.text,
        timestamp=ctx_meta.timestamp
    )

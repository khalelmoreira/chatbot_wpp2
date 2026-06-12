from src.types.context_tomador import ContextTomador
from src.managers.conversation_manager import ConversationManager
from src.models.conversation_state import ConversationStatus
from src.flows.fluxo_collecting import fluxo_collecting
from src.utils.debug import print_table
from src.types.incoming_msg import IncomingMessage
from src.flows.fluxo_confirming import fluxo_confirming

def fluxo_ativo_dispatcher(ctx: ContextTomador, ctx_meta: IncomingMessage):

    print(f"\n\n----------------TESTE FLUXO ATIVO_DISPATCHER----------------\n\n")

    conversation = ConversationManager()
    conversa = conversation.get_ativa(ctx.user.id)
    print(f"CONVERSA: {conversa}\n") if conversa is None else print(f"CONVERSA: {dict(conversa)}\n")

    if not conversa:
        return fluxo_collecting(ctx, conversation)

    else:
        ctx.conversation_id = conversa["id"]
        print(f"CTX.CONVERSATION_ID: {ctx.conversation_id}\n")

    status = conversa["status"] if conversa else None
    print(f"STATUS: {status}\n")

    match status:

        case None | "COLLECTING":
            return fluxo_collecting(ctx, conversation)
            
        case "CONFIRMING":
            return fluxo_confirming(ctx, conversation, ctx_meta)

        case "QUEUED":
            conversation.emitting()

        case _:
            raise ValueError(f"Estado não mapeado no fluxo: {status}")

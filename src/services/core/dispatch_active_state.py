from src.types import ContextTomador, IncomingMessage
from src.managers.conversation_manager import ConversationManager
from src.types.conversation_state import ConversationStatus
from src.flows.collecting_flow import fluxo_collecting
from src.utils.debug import print_table
from src.flows.confirming_flow import fluxo_confirming
from src.flows.queued_flow import fluxo_queued

def dispatch_active_state(ctx: ContextTomador, msg: IncomingMessage):

    print(f"\n\n----------------TESTE FLUXO ATIVO_DISPATCHER----------------\n\n")

    conversation = ConversationManager(ctx)
    conversa = conversation.get_ativa()
    print(f"CONVERSA: {conversa}\n") if conversa is None else print(f"CONVERSA: {dict(conversa)}\n")

    if not conversa:
        return fluxo_collecting(ctx, conversation)

    else:
        ctx.conversation_id = conversa["id"]
        print(f"CTX.CONVERSATION_ID: {ctx.conversation_id}\n")

    status = conversa["status"] if conversa else None
    print(f"STATUS: {status}\n")

    match status:

        case None | ConversationStatus.COLLECTING:
            return fluxo_collecting(ctx, conversation)
            
        case ConversationStatus.CONFIRMING:
            return fluxo_confirming(ctx, conversation, msg)

        case ConversationStatus.QUEUED:
            fluxo_queued(ctx, conversation)

        case _:
            raise ValueError(f"Estado não mapeado no fluxo: {status}")

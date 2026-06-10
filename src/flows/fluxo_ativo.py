from src.types.context_tomador import ContextTomador
from src.managers.conversation_manager import ConversationManager
from src.models.conversation_state import ConversationStatus
from src.flows.fluxo_collecting import fluxo_collecting

def fluxo_ativo_dispatcher(ctx: ContextTomador):

    conversation = ConversationManager()
    status = conversation.get_status(ctx.user.phone)

    if status is None:
        return fluxo_collecting(ctx, conversation)

    match ConversationStatus(status):
        
        case ConversationStatus.COLLECTING:
            return fluxo_collecting(ctx, conversation)

        case ConversationStatus.CONFIRMING:
            conversation.confirming()

        case ConversationStatus.EMITTING:
            conversation.emitting()

        case ConversationStatus.DONE:
            return
        
        case ConversationStatus.ERROR:
            conversation.error()

        case ConversationStatus.CANCELLED:
            conversation.cancelled()

        case _:
            raise ValueError(f"Estado não mapeado no fluxo: {status}")

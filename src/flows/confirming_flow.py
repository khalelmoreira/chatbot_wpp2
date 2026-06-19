from src.managers.conversation_manager import ConversationManager
from src.types import ContextTomador, IncomingMessage
from src.services.confirming.confirming_service import ConfirmingService

def fluxo_confirming(ctx: ContextTomador, conversation: ConversationManager, msg: IncomingMessage) -> None:

    print(f"\n\n----------------TESTE FLUXO CONFIRMING----------------\n\n")
    
    confirming = ConfirmingService(ctx, msg, conversation)
    confirming.dispatch()
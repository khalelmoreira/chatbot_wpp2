from chatbot_wpp2.src.managers.conversations.conv_manager import ConversationManager
from src.types import ContextTomador, IncomingMessage
from chatbot_wpp2.src.services.active.confirming.confirming_service import ConfirmingService

def confirming_flow(ctx: ContextTomador, conversation: ConversationManager, msg: IncomingMessage) -> None:

    print(f"\n\n----------------TESTE FLUXO CONFIRMING----------------\n\n")
    
    confirming = ConfirmingService(ctx, msg, conversation)
    confirming.dispatch()
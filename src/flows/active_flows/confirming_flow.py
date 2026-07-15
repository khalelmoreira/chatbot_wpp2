from src.managers.conversations.conv_manager import ConvManager
from src.types import ContextTomador, IncomingMessage
from src.services.active.confirming.confirming_service import ConfirmingService

def confirming_flow(ctx: ContextTomador, conversation: ConvManager) -> None:

    print(f"\n\n----------------TESTE FLUXO CONFIRMING----------------\n\n")
    
    confirming = ConfirmingService(ctx, conversation)
    confirming.dispatch()
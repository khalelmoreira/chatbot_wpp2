from src.managers.conversations.conv_manager import ConvManager
from src.services.active.confirming.confirming_service import ConfirmingService
from src.types import ContextTomador


def confirming_flow(ctx: ContextTomador, conversation: ConvManager) -> None:

    print("\n\n----------------TESTE FLUXO CONFIRMING----------------\n\n")
    
    confirming = ConfirmingService(ctx, conversation)
    confirming.dispatch()
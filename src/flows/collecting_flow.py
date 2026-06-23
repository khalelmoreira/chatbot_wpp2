from src.services.collecting.collecting_service import CollectingService
from src.managers.conversations.conversation_manager import ConversationManager
from src.types import ContextTomador

def collecting_flow(ctx: ContextTomador, conversation: ConversationManager) -> None:
    
    print(f"\n\n----------------TESTE FLUXO COLLECTING----------------\n\n")

    collecting = CollectingService(ctx, conversation)
    conv = collecting.criar_conv_se()
    
    if conv:
        collecting.extract_e_merge()
        collecting.valido_e_completo()

    else:
        return
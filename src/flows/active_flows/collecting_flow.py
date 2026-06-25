from src.services.collecting.collecting_service import CollectingService, IntentService, ExtractionService
from src.managers.conversations.conversation_manager import ConversationManager
from src.types import ContextTomador

def collecting_flow(ctx: ContextTomador, conversation: ConversationManager) -> None:
    
    print(f"\n\n----------------TESTE FLUXO COLLECTING----------------\n\n")

    intent = IntentService(ctx, conversation)
    extraction = ExtractionService(ctx, conversation)
    collecting = CollectingService(ctx, conversation)

    conv = intent.criar_conv_se()
    if conv:
        intent.handle_active(extraction)

    
    if conv:
        collecting.extract_e_merge()
        collecting.valido_e_completo()

    else:
        return
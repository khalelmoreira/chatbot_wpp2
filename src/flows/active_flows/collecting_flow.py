from src.services.collecting.collecting_service import IntentService, ExtractionService, ValidationService
from src.managers.conversations.conversation_manager import ConversationManager
from src.types import ContextTomador

def collecting_flow(ctx: ContextTomador, conversation: ConversationManager) -> None:
    
    print(f"\n\n----------------TESTE FLUXO COLLECTING----------------\n\n")

    intent = IntentService(ctx, conversation)
    if not intent.criar_conv_se():
        return
    
    ExtractionService(ctx, conversation).extract_e_merge()
    ValidationService(ctx, conversation).valido_e_completo()
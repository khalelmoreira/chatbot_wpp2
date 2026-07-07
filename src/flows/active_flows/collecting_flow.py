from chatbot_wpp2.src.services.active.collecting.collecting_service import ExtractionService, ValidationService
from chatbot_wpp2.src.managers.conversations.conv_manager import ConversationManager
from src.types import ContextTomador

def collecting_flow(ctx: ContextTomador, conversation: ConversationManager) -> None:
    
    print(f"\n\n----------------TESTE FLUXO COLLECTING----------------\n\n")
    
    ExtractionService(ctx, conversation).extract_e_merge()
    ValidationService(ctx, conversation).valido_e_completo()
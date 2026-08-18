from src.managers.conversations.conv_manager import ConvManager
from src.services.active.collecting.collecting_service import ExtractionService, ValidationService
from src.types import ContextTomador


def collecting_flow(ctx: ContextTomador, conversation: ConvManager) -> None:
    
    print("\n\n----------------TESTE FLUXO COLLECTING----------------\n\n")
    
    ExtractionService(ctx, conversation).extract_e_merge()
    ValidationService(ctx, conversation).valido_e_completo()
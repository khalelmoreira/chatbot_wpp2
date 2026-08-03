from src.services.sign_up.address_service import ExtractionService, ValidationService
from src.types import UserStatus, ContextPrestador
from src.managers.user_manager import PrestadorManager

def address_flow(ctx: ContextPrestador):
    
    print(f"\n\n----------------TESTE FLUXO ADDRESS----------------\n\n")
    print(f"CTX: {ctx}\n")

    prestador = PrestadorManager(ctx)
    validation = ValidationService(ctx, prestador)

    ExtractionService(ctx, prestador).extract_e_merge()

    if not validation.valido():
        return
    
    if not validation.completo():
        return
    
    prestador.update_state(UserStatus.CONFIRMING)
    validation.msg_confirm()
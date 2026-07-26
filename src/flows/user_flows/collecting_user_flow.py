from src.types import ContextPrestador
from src.managers.user_manager import PrestadorManager
from src.services.sign_up.collecting_user_service import ExtractionService, ValidationService, AddressService

def collecting_flow(ctx: ContextPrestador) -> None:

    print(f"\n\n----------------TESTE FLUXO PREST COLLECTING----------------\n\n")

    prestador = PrestadorManager(ctx)
    validation = ValidationService(ctx, prestador)
    
    ExtractionService(ctx, prestador).extract_e_merge()

    if not validation.valido():
        return
    
    if not validation.completo():
        return
    
    AddressService(ctx, prestador).address()
from src.types import ContextPrestador
from src.managers.prestador_manager import PrestadorManager
from src.services.sign_up.collecting.collecting_user_service import ExtractionService, ValidationService, AddressService

def collecting_flow(ctx: ContextPrestador, prestador: PrestadorManager) -> None:

    print(f"\n\n----------------TESTE FLUXO PREST COLLECTING----------------\n\n")

    ExtractionService(ctx, prestador).extract_e_merge()
    validation = ValidationService(ctx, prestador)

    valido = validation.valido()
    if not valido:
        return
    
    completo = validation.completo()
    if not completo:
        return
    
    AddressService(ctx, prestador).address()
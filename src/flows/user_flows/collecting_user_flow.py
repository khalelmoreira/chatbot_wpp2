from src.types import ContextPrestador
from src.managers.prestador_manager import PrestadorManager
from chatbot_wpp2.src.services.sign_up.collecting_user_service import ExtractionService, ValidationService, AddressService

def collecting_flow(ctx: ContextPrestador) -> None:

    print(f"\n\n----------------TESTE FLUXO PREST COLLECTING----------------\n\n")

    ExtractionService(ctx).extract_e_merge()
    
    prestador = PrestadorManager(ctx)
    validation = ValidationService(ctx, prestador)

    valido = validation.valido()
    if not valido:
        return
    
    completo = validation.completo()
    if not completo:
        return
    
    AddressService(ctx, prestador).address()
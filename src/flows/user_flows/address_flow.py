from src.services.sign_up.collecting.address_service import ExtractionService, ValidationService
from src.types import IncomingMessage, UserStatus, ContextPrestador
from chatbot_wpp2.src.managers.prestador_manager import PrestadorManager

def address_flow(ctx: ContextPrestador, msg: IncomingMessage, prestador: PrestadorManager):
    
    print(f"\n\n----------------TESTE FLUXO ADDRESS----------------\n\n")

    ExtractionService(ctx, prestador).extract_e_merge()
    validation = ValidationService(ctx, prestador)

    valido = validation.valido()
    if not valido:
        return
    
    completo = validation.completo()
    if not completo:
        return
    prestador.update_state(UserStatus.CONFIRMING)
    validation.msg_confirm()
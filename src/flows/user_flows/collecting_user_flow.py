from src.managers.user_manager import PrestadorManager
from src.services.sign_up.collecting_user_service import (
    AddressService,
    CnpjService,
    ExtractionService,
    ValidationService,
)
from src.types import ContextPrestador


def collecting_flow(ctx: ContextPrestador) -> None:

    print("\n\n----------------TESTE FLUXO PREST COLLECTING----------------\n\n")
    print(f"CTX: {ctx}\n")

    prestador = PrestadorManager(ctx)
    validation = ValidationService(ctx, prestador)

    ExtractionService(ctx, prestador).extract_e_merge()

    if not validation.valido():
        return

    if not validation.completo():
        return

    if not CnpjService(ctx, prestador).verificar():
        return

    AddressService(ctx, prestador).address()
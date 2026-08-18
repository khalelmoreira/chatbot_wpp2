from src.managers.user_manager import PrestadorManager
from src.services.sign_up.confirming_user_service import ConfirmUserService
from src.types import ContextPrestador


def confirming_flow(ctx: ContextPrestador) -> None:

    print("\n\n----------------CONFIRMING USER FLOW----------------\n\n")
    print(f"CTX: {ctx}\n")
    
    prestador = PrestadorManager(ctx)
    ConfirmUserService(ctx, prestador).dispatch()
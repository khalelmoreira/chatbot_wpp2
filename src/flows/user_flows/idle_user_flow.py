from src.managers.user_manager import PrestadorManager
from src.services.sign_up.intent_user_service import IntentUserService
from src.types import ContextPrestador


def idle_user_flow(ctx: ContextPrestador):

    print("\n\n----------------IDLE USER FLOW----------------\n\n")
    print(f"CTX: {ctx}\n")

    conv = PrestadorManager(ctx)
    intent = IntentUserService(ctx, conv)

    intencao = intent.intent()
    intent.dispatch_intent(intencao)
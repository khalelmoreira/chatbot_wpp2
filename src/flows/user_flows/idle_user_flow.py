from src.services.active.intent_service import IntentService
from src.types import ContextPrestador

def idle_user_flow(ctx: ContextPrestador):

    print(f"\n\n----------------IDLE USER FLOW----------------\n\n")

    intent = IntentService(ctx)
    intencao = intent.intent()
    intent.dispatch_intent(intencao)
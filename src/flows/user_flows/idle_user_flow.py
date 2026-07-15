from src.managers.conversations.conv_manager import ConvManager
from src.services.sign_up.intent_user_service import IntentUserService
from src.types import ContextPrestador

def idle_user_flow(ctx: ContextPrestador):

    print(f"\n\n----------------IDLE USER FLOW----------------\n\n")

    conv = ConvManager(ctx)
    intent = IntentUserService(ctx, conv)

    intencao = intent.intent()
    intent.dispatch_intent(intencao)
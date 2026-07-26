from src.services.active.intent_service import IntentService
from src.types import ContextTomador
from src.managers.conversations import ConvManager

def idle_flow(ctx: ContextTomador, conversation: ConvManager):

    print(f"\n\n----------------IDLE FLOW----------------\n\n")

    intent = IntentService(ctx, conversation)
    intencao = intent.intent()
    intent.dispatch_intent(intencao)
from src.managers.conversations import ConvManager
from src.services.active.intent_service import IntentService
from src.types import ContextTomador


def idle_flow(ctx: ContextTomador, conversation: ConvManager):

    print("\n\n----------------IDLE FLOW----------------\n\n")

    intent = IntentService(ctx, conversation)
    intencao = intent.intent()
    intent.dispatch_intent(intencao)
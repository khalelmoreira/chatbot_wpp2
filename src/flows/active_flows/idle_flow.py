from src.services.active.intent_service import IntentService
from src.types import ContextTomador
from src.managers.conversations import ConversationManager

def idle_flow(ctx: ContextTomador, conversation: ConversationManager):

    print(f"\n\n----------------IDLE FLOW----------------\n\n")

    intent = IntentService(ctx, conversation)
    intencao = intent.intent()
    intent.dispatch_intent(intencao)
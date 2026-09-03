import logging

from src.managers.user_manager import PrestadorManager
from src.services.sign_up.greeting_service import GreetingService
from src.services.sign_up.intent_user_service import IntentUserService
from src.types import ContextPrestador

logger = logging.getLogger(__name__)

def idle_user_flow(ctx: ContextPrestador):

    logger.debug("idle_user_flow: user_id=%s", ctx.user.id)

    conv = PrestadorManager(ctx)

    # Clique nos botões da saudação ("🚀 Começar" / "📖 Como funciona") — resolvido
    # de forma determinística, nunca passa pelo classificador de intenção.
    if GreetingService(ctx, conv).handle_button():
        return

    intent = IntentUserService(ctx, conv)
    intent.dispatch_intent(intent.intent())

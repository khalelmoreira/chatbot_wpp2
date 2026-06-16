from src.types.context_tomador import ContextTomador
from src.managers.conversation_manager import ConversationManager
from src.services.shared.msg_service import send_msg_text

def fluxo_queued(ctx: ContextTomador, conversation: ConversationManager):
    send_msg_text(
        ctx.user.phone,
        "⏳ Sua nota já está na fila de emissão. Aguarde, te aviso assim que sair!"
    )
    return